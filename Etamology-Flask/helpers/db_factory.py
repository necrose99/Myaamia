# helpers/db_factory.py
"""
Unified Database & RDF Store Wrangler for Algic Etymology Engine.
Handles SQL (SQLite, MySQL, Postgres), NoSQL (MongoDB), Cache (Redis),
and RDF/SPARQL Graph persistence under a dynamic configuration model.
"""

import os
import logging
import sqlite3
from typing import Optional, Dict, Any, Union
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
import redis
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DBWrangler")

# Core Extensions (Singletons)
db_sql = SQLAlchemy()
db_mongo = PyMongo()
# helpers/db_factory.py
import sqlite3
from helpers.db_factory_ipa import init_ipa_schema, sync_tmx_to_db
from helpers.db_factory_audio import update_audio_mapping, fetch_all_lexical_rows

class DatabaseFactory:
    def __init__(self, db_path: str = 'data/olac_data.db'):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            init_ipa_schema(conn)

    def import_tmx(self, tmx_path: str, g2p_func, voice_profile_func):
        with self.get_connection() as conn:
            return sync_tmx_to_db(conn, tmx_path, g2p_func, voice_profile_func)

    def bind_audio(self, word: str, audio_url: str):
        with self.get_connection() as conn:
            update_audio_mapping(conn, word, audio_url)

    def get_lexical_entries(self):
        with self.get_connection() as conn:
            return fetch_all_lexical_rows(conn)

class RedisManager:
    """Safely encapsulates Redis connection handling."""
    def __init__(self):
        self.client: Optional[redis.Redis] = None

    def init_app(self, host: str = "localhost", port: int = 6379, db: int = 0):
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True
            )
            # Test connectivity
            self.client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}. Running without Redis cache.")
            self.client = None

    def get_client(Cpu) -> Optional[redis.Redis]:
        return self.client


class RDFStoreManager:
    """
    Manages RDF/Turtle serialization, graph storage, and SPARQL execution.
    Acts as the persistence layer for sparql_plugin.py.
    """

    def __init__(self, ttl_path: str = "data/algic_graph.ttl"):
        self.ttl_path = ttl_path
        self.graph = Graph()
        self._ensure_storage_dir()
        self.load_graph()

    def _ensure_storage_dir(self):
        """Ensures storage directory exists."""
        directory = os.path.dirname(self.ttl_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def load_graph(self):
        """Loads existing TTL store into memory or initializes a fresh one."""
        if os.path.exists(self.ttl_path):
            try:
                self.graph.parse(self.ttl_path, format="turtle")
                logger.info(f"Loaded {len(self.graph)} triples from {self.ttl_path}")
            except Exception as e:
                logger.error(f"Failed to load TTL store at {self.ttl_path}: {e}")
        else:
            logger.info(f"No existing TTL store found at {self.ttl_path}. Initializing empty graph.")

    def save_graph(self) -> bool:
        """Persists memory graph back to Turtle (.ttl) format on disk."""
        try:
            self.graph.serialize(destination=self.ttl_path, format="turtle")
            logger.info(f"Persisted {len(self.graph)} triples to {self.ttl_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save TTL graph: {e}")
            return False

    def query(self, sparql_query: str) -> list:
        """Executes SPARQL query against stored RDF graph."""
        results = self.graph.query(sparql_query)
        output = []
        for row in results:
            output.append({str(k): str(v) for k, v in row.asdict().items()})
        return output

    def add_triple(self, s: URIRef, p: URIRef, o: Union[URIRef, Literal]):
        """Adds a single triple and auto-commits to disk."""
        self.graph.add((s, p, o))

    def merge_graph(self, incoming_graph: Graph) -> int:
        """Merges external RDF graph and auto-saves."""
        initial_len = len(self.graph)
        self.graph += incoming_graph
        added = len(self.graph) - initial_len
        logger.info(f"Merged {added} new triples into RDF store.")
        self.save_graph()
        return added


class RelationalCacheManager:
    """
    SQLite/SQL relational backend for fast indexing of ISO languages, 
    Glottolog URIs, and tracking upstream fetch sync states.
    """

    def __init__(self, db_path: str = "data/algic_metadata.db"):
        self.db_path = db_path
        self._ensure_dir()
        self._init_db()

    def _ensure_dir(self):
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes relational tables for cached language metadata and ingestion logs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS languages (
                    iso_code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    subgroup TEXT NOT NULL,
                    glottocode TEXT,
                    glottolog_ttl_url TEXT,
                    last_synced TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fetch_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resource_key TEXT NOT NULL,
                    url TEXT NOT NULL,
                    triples_added INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            logger.info("Relational metadata database initialized.")

    def register_language(self, iso: str, name: str, group: str, glottocode: Optional[str] = None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO languages (iso_code, name, subgroup, glottocode)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(iso_code) DO UPDATE SET
                    name=excluded.name,
                    subgroup=excluded.subgroup,
                    glottocode=excluded.glottocode
            """, (iso, name, group, glottocode))
            conn.commit()

    def log_fetch(self, key: str, url: str, triples_added: int, status: str = "SUCCESS"):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fetch_logs (resource_key, url, triples_added, status)
                VALUES (?, ?, ?, ?)
            """, (key, url, triples_added, status))
            conn.commit()


class DBWrangler:
    """
    Unified Database & Persistence Wrangler.
    Encapsulates SQL, Mongo, Redis, and RDF store management into one clean, 
    dynamically configurable instance.
    """

    def __init__(self, app: Optional[Flask] = None, data_dir: str = "data"):
        self.data_dir = data_dir
        self.redis_mgr = RedisManager()
        self.rdf_store: Optional[RDFStoreManager] = None
        self.relational_cache: Optional[RelationalCacheManager] = None
        self.app: Optional[Flask] = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Dynamic database initialization based on app.config or environment variables."""
        self.app = app
        db_type = app.config.get("DB_TYPE", os.getenv("DB_TYPE", "sqlite")).lower()

        # 1. SQL Backend Setup (SQLAlchemy)
        if db_type == "sqlite":
            app.config.setdefault('SQLALCHEMY_DATABASE_URI', f"sqlite:///{os.path.join(self.data_dir, 'algic_app.db')}")
        elif db_type == "mysql":
            app.config.setdefault('SQLALCHEMY_DATABASE_URI', os.getenv("MYSQL_URI", "mysql+pymysql://user:pass@localhost/algic"))
        elif db_type == "postgresql":
            app.config.setdefault('SQLALCHEMY_DATABASE_URI', os.getenv("POSTGRES_URI", "postgresql+psycopg2://user:pass@localhost/algic"))

        app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
        db_sql.init_app(app)

        # 2. NoSQL Mongo Setup
        if db_type == "mongodb" or app.config.get("USE_MONGO", False):
            app.config.setdefault("MONGO_URI", os.getenv("MONGO_URI", "mongodb://localhost:27017/algicEtymology"))
            db_mongo.init_app(app)

        # 3. Redis Cache Setup
        if app.config.get("USE_REDIS", False) or os.getenv("USE_REDIS") == "true":
            redis_host = app.config.get("REDIS_HOST", os.getenv("REDIS_HOST", "localhost"))
            redis_port = int(app.config.get("REDIS_PORT", os.getenv("REDIS_PORT", 6379)))
            self.redis_mgr.init_app(host=redis_host, port=redis_port)

        # 4. RDF Store & Relational Metadata Setup
        ttl_path = os.path.join(self.data_dir, app.config.get("TTL_FILENAME", "algic_graph.ttl"))
        db_path = os.path.join(self.data_dir, app.config.get("METADATA_DB_FILENAME", "algic_metadata.db"))

        self.rdf_store = RDFStoreManager(ttl_path=ttl_path)
        self.relational_cache = RelationalCacheManager(db_path=db_path)

        logger.info(f"DBWrangler successfully initialized for engine target: [{db_type.upper()}]")

    def reconfigure(self, new_config: Dict[str, Any]):
        """Dynamically reconfigures database URIs and connections from an admin/config update."""
        if not self.app:
            raise RuntimeError("Cannot reconfigure DBWrangler without an active Flask app context.")

        self.app.config.update(new_config)
        self.init_app(self.app)
        logger.info("DBWrangler reconfigured dynamically.")


# Global Singleton Factory Access
_wrangler_instance: Optional[DBWrangler] = None


def get_db_wrangler(app: Optional[Flask] = None, data_dir: str = "data") -> DBWrangler:
    """Returns or creates the global singleton instance of DBWrangler."""
    global _wrangler_instance
    if _wrangler_instance is None:
        _wrangler_instance = DBWrangler(app=app, data_dir=data_dir)
    elif app is not None and _wrangler_instance.app is None:
        _wrangler_instance.init_app(app)
    return _wrangler_instance


def init_databases(app: Flask) -> DBWrangler:
    """Primary initialization entry point for app.py."""
    return get_db_wrangler(app=app)
	# helpers/db_factory.py
import sqlite3
from helpers.db_factory_core import init_core_db, get_core_db_connection, check_export_permission
from helpers.db_factory_ipa import init_ipa_schema, sync_tmx_to_db
from helpers.db_factory_audio import update_audio_mapping, fetch_all_lexical_rows

class AlgicDbWrangler:
    """Unified database wrangler handling core etymology, IPA, and audio connections."""

    def __init__(self, db_path: str = "data/olac_data.db"):
        self.db_path = db_path
        self.admin_api_key = init_core_db(self.db_path)
        
        # Initialize sub-schemas
        with self.get_connection() as conn:
            init_ipa_schema(conn)

    def get_connection(self) -> sqlite3.Connection:
        return get_core_db_connection(self.db_path)

    def can_export(self, role: str, fmt: str) -> bool:
        with self.get_connection() as conn:
            return check_export_permission(conn, role, fmt)

    def import_tmx(self, tmx_path: str, g2p_func, voice_profile_func):
        with self.get_connection() as conn:
            return sync_tmx_to_db(conn, tmx_path, g2p_func, voice_profile_func)

    def get_lexical_entries(self):
        with self.get_connection() as conn:
            return fetch_all_lexical_rows(conn)

def init_databases(app) -> AlgicDbWrangler:
    """Bootstraps database configuration onto the Flask application."""
    db_path = app.config.get("SQLITE_DB_PATH", "data/olac_data.db")
    wrangler = AlgicDbWrangler(db_path)
    app.config["ADMIN_API_KEY"] = wrangler.admin_api_key
    return wrangler

# Mock stubs for SQLAlchemy/Mongo compatibility if needed in app context
class DummySqlAlchemy:
    def create_all(self):
        pass

db_sql = DummySqlAlchemy()
db_mongo = None