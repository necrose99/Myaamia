# helpers/db_factory_core.py
"""
helpers/db_factory_core.py
==========================
Core database factory, schema initializations, Algic language registry seeding,
OLAC metadata store definitions, and user export permissions management.
"""

import secrets
import sqlite3
import uuid
from typing import Dict, Any, Optional

# ── Expanded Algic Language Registry ─────────────────────────────────────────
ALGIC: Dict[str, Dict[str, Any]] = {
    # --- Plains Algonquian ---
    "bft": {"name": "Blackfoot",           "branch": "Plains",   "script": "roman"},
    "arp": {"name": "Arapaho",             "branch": "Plains",   "script": "roman"},
    "ats": {"name": "Gros Ventre",         "branch": "Plains",   "script": "roman"},
    "chy": {"name": "Cheyenne",            "branch": "Plains",   "script": "roman"},

    # --- Central Algonquian ---
    "men": {"name": "Menominee",           "branch": "Central",  "script": "roman"},
    "cre": {"name": "Plains/Woods Cree",   "branch": "Central",  "script": "syllabics", "priority": True},
    "csw": {"name": "Swampy Cree",         "branch": "Central",  "script": "syllabics"},
    "crj": {"name": "Southern East Cree", "branch": "Central",  "script": "syllabics"},
    "atj": {"name": "Atikamekw",           "branch": "Central",  "script": "roman"},
    "pot": {"name": "Potawatomi",          "branch": "Central",  "script": "roman",     "priority": True},
    "oji": {"name": "Ojibwe",              "branch": "Central",  "script": "roman"},
    "otw": {"name": "Ottawa",              "branch": "Central",  "script": "roman"},
    "ciw": {"name": "Chippewa",            "branch": "Central",  "script": "roman"},
    "mia": {"name": "Miami-Illinois",      "branch": "Central",  "script": "roman",     "priority": True},
    "sac": {"name": "Meskwaki (Fox)",      "branch": "Central",  "script": "roman",     "priority": True},
    "kic": {"name": "Kickapoo",            "branch": "Central",  "script": "roman",     "priority": True},
    "sjw": {"name": "Shawnee",             "branch": "Central",  "script": "roman"},

    # --- Eastern Algonquian ---
    "mic": {"name": "Mi'kmaq",             "branch": "Eastern",  "script": "roman"},
    "abe": {"name": "Western Abenaki",     "branch": "Eastern",  "script": "roman"},
    "aaq": {"name": "Eastern Abnaki",      "branch": "Eastern",  "script": "roman"},
    "mal": {"name": "Maliseet-Passamaquoddy", "branch": "Eastern", "script": "roman"},
    "moo": {"name": "Mohegan-Pequot",      "branch": "Eastern",  "script": "roman"},
    "mua": {"name": "Munsee",              "branch": "Eastern",  "script": "roman"},
    "unm": {"name": "Unami",               "branch": "Eastern",  "script": "roman"},

    # --- Ritwan & Western Algic Sister Languages ---
    "yur": {"name": "Yurok",               "branch": "Ritwan",   "script": "roman"},
    "wiy": {"name": "Wiyot",               "branch": "Ritwan",   "script": "roman"},

    # --- Proto-Languages ---
    "alg-x-proto": {"name": "Proto-Algonquian★", "branch": "Proto", "script": "roman"},

    # --- Lost / Unattested / Remnant Languages ---
    "bue": {"name": "Beothuk (Remnant)",   "branch": "Remnant",  "script": "roman",     "remnant": True},
    "etc": {"name": "Etchemin (Remnant)",  "branch": "Remnant",  "script": "roman",     "remnant": True},
    "xlo": {"name": "Loup A (Mots loups)", "branch": "Remnant",  "script": "roman",     "remnant": True},
    "xlb": {"name": "Loup B (Remnant)",    "branch": "Remnant",  "script": "roman",     "remnant": True},
    "crr": {"name": "Lumbee / Pamlico",    "branch": "Remnant",  "script": "roman",     "remnant": True},
    "pim": {"name": "Powhatan (Virginia)", "branch": "Remnant",  "script": "roman",     "remnant": True},
    "qyp": {"name": "Quiripi / Naugatuck", "branch": "Remnant",  "script": "roman",     "remnant": True},

    # --- Dialect/Locale Cross-Keys & Gloss Auxiliary Languages ---
    "kic_mx": {"name": "Kickapoo (Coahuila, MX)", "branch": "Central", "script": "roman", "priority": True},
    "eng":    {"name": "English (Meta/Gloss)",   "branch": "Auxiliary", "script": "roman"},
    "spa":    {"name": "Spanish (Meta/Gloss)",   "branch": "Auxiliary", "script": "roman"},
    "es_mx":  {"name": "Spanish (Mexican Meta)",  "branch": "Auxiliary", "script": "roman"},
    "fra":    {"name": "French (Meta/Gloss)",    "branch": "Auxiliary", "script": "roman"},
    "fro":    {"name": "Old French (Gloss)",     "branch": "Auxiliary", "script": "roman"}
}

# ── Unified Core SQL Schema ────────────────────────────────────────────────────
SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Language Registry Table
CREATE TABLE IF NOT EXISTS languages (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    branch TEXT NOT NULL,
    script TEXT DEFAULT 'roman',
    priority INTEGER DEFAULT 0,
    remnant INTEGER DEFAULT 0
);

-- Access Control & Users
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    api_key TEXT UNIQUE,
    created TEXT DEFAULT (datetime('now'))
);

-- Lexical Entries
CREATE TABLE IF NOT EXISTS entries (
    id TEXT PRIMARY KEY,
    lang TEXT NOT NULL REFERENCES languages(code),
    form TEXT NOT NULL,
    ipa TEXT,
    pos TEXT,
    gloss_en TEXT,
    gloss_fr TEXT,
    gloss_es TEXT,
    proto_form TEXT,
    morph_seg TEXT,
    source_url TEXT,
    source_type TEXT,
    confidence REAL DEFAULT 0.5,
    media_urls TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Cognate Sets & Members
CREATE TABLE IF NOT EXISTS cognate_sets (
    id TEXT PRIMARY KEY,
    proto_form TEXT,
    proto_gloss TEXT,
    confidence REAL DEFAULT 0.7,
    source_ref TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS cognate_members (
    set_id TEXT REFERENCES cognate_sets(id) ON DELETE CASCADE,
    entry_id TEXT REFERENCES entries(id) ON DELETE CASCADE,
    PRIMARY KEY (set_id, entry_id)
);

-- Example Sentences
CREATE TABLE IF NOT EXISTS examples (
    id TEXT PRIMARY KEY,
    entry_id TEXT REFERENCES entries(id) ON DELETE CASCADE,
    sentence TEXT,
    translation TEXT,
    lang_trans TEXT DEFAULT 'en',
    source TEXT
);

-- Open Language Archives Community (OLAC) Records
CREATE TABLE IF NOT EXISTS olac_records (
    id TEXT PRIMARY KEY,
    oai_id TEXT,
    title TEXT,
    description TEXT,
    lang TEXT,
    rights TEXT,
    source_repo TEXT,
    raw_xml TEXT,
    harvested_at TEXT DEFAULT (datetime('now'))
);

-- Import & Ingest Logs
CREATE TABLE IF NOT EXISTS import_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT DEFAULT (datetime('now')),
    username TEXT,
    action TEXT,
    source TEXT,
    records_in INTEGER DEFAULT 0,
    records_new INTEGER DEFAULT 0
);

-- Export Format Authorization
CREATE TABLE IF NOT EXISTS export_permissions (
    role TEXT,
    format TEXT,
    PRIMARY KEY (role, format)
);

-- Speed Indexes
CREATE INDEX IF NOT EXISTS idx_entries_lang ON entries(lang);
CREATE INDEX IF NOT EXISTS idx_entries_form ON entries(form);
CREATE INDEX IF NOT EXISTS idx_examples_entry ON examples(entry_id);
"""

# Default export permissions matrix for different roles
DEFAULT_EXPORT_PERMS = [
    ("admin", "tmx"), ("admin", "xliff"), ("admin", "lift"), ("admin", "eaf"),
    ("admin", "tei"), ("admin", "stardict"), ("admin", "json"), ("admin", "csv"),
    ("admin", "sql"), ("admin", "ollama-jsonl"),
    ("user", "tmx"), ("user", "json"), ("user", "csv")
]

# OLAC Namespace Metadata Constants
OLAC_SCHEMAS: Dict[str, str] = {
    "olac": "http://language-archives.org",
    "dc": "http://purl.org",
}
NS_OAI = "http://openarchives.org"
NS_DC = "http://purl.org"
NS_OAIDC = "http://openarchives.org/OAI/2.0/oai_dc/"


def get_core_db_connection(db_path: str) -> sqlite3.Connection:
    """
    Returns an active SQLite connection configured with `check_same_thread=False`
    and `Row` factory for multi-threaded usage across Flask and background tasks.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def seed_languages(conn: sqlite3.Connection) -> None:
    """Populates or updates the `languages` table using the `ALGIC` registry dict."""
    cursor = conn.cursor()
    for code, meta in ALGIC.items():
        cursor.execute(
            """
            INSERT INTO languages (code, name, branch, script, priority, remnant)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
                name=excluded.name,
                branch=excluded.branch,
                script=excluded.script,
                priority=excluded.priority,
                remnant=excluded.remnant
            """,
            (
                code,
                meta.get("name", ""),
                meta.get("branch", "Unknown"),
                meta.get("script", "roman"),
                1 if meta.get("priority") else 0,
                1 if meta.get("remnant") else 0,
            ),
        )


def init_core_db(db_path: str) -> str:
    """
    Executes the base schema, populates export permissions, seeds the Algic language
    registry, sets up default admin credentials, and returns the admin API key.
    """
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)

    # Seed language metadata table
    seed_languages(conn)

    # Seed default export permissions
    for role, fmt in DEFAULT_EXPORT_PERMS:
        conn.execute("INSERT OR IGNORE INTO export_permissions VALUES(?,?)", (role, fmt))

    # Seed default admin user if absent
    admin_row = conn.execute("SELECT api_key FROM users WHERE username='admin'").fetchone()
    if admin_row and admin_row[0]:
        admin_key = admin_row[0]
    else:
        admin_id = str(uuid.uuid4())
        admin_key = secrets.token_hex(16)
        conn.execute(
            "INSERT OR REPLACE INTO users(id, username, role, api_key) VALUES(?,?,?,?)",
            (admin_id, "admin", "admin", admin_key)
        )

    conn.commit()
    conn.close()
    return admin_key


def check_export_permission(conn: sqlite3.Connection, role: str, fmt: str) -> bool:
    """Validates whether a given user role is authorized to export data in the specified target format."""
    cur = conn.cursor()
    row = cur.execute(
        "SELECT 1 FROM export_permissions WHERE role = ? AND format = ?", (role, fmt)
    ).fetchone()
    return row is not None


def db(db_path: str) -> sqlite3.Connection:
    """Legacy helper function for direct connection acquisition."""
    return get_core_db_connection(db_path)