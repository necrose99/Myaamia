import os
import sys

# Ensure local helpers directory is in the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/helpers"))

from flask import Flask, request, jsonify, Response

# Centralized application configuration
from Admin import cfg

# Core Flask extensions and search
from flask_apcore import APCore
from flask_alembic import Alembic
from flask_whooshee import Whooshee 

# Data architecture integrations
from flask_apialchemy import APIAlchemy
from flask_redis import FlaskRedis
from flask_mongoengine import MongoEngine 

# RDF & SPARQL requirements
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import FOAF, RDF, OWL
from flask_rdf.flask import returns_rdf

# Multi-DB Factory layer imports
from helpers import db_factory_redis
from helpers.db_factory import init_databases, db_sql, db_mongo

# Initialize the single core application instance
app = Flask(__name__)

# Core Defaults (Can be dynamically hot-swapped by the router if SQLite gets too large)
app.config["DB_TYPE"] = "sqlite"  
app.config["USE_REDIS"] = True
app.config["SQLITE_MAX_SIZE_MB"] = 500  

# Apply centralized settings and plugins from Admin.cfg
app.config.from_object(cfg)

# Boot unified databases & RDF store manager
wrangler = init_databases(app)

# Initialize application infrastructure extensions
apcore = APCore(app)
alembic = Alembic(app)
whooshee = Whooshee(app)
db_alchemy = APIAlchemy(app)

# Optional cache layer
redis_client = FlaskRedis(app) if app.config["USE_REDIS"] else None

# Global semantic graph instance (backed by wrangler/SQLite/Mongo or loaded dynamically)
semantic_store = Graph()

# Nginx/Apache Header Middleware: Captures real client routing signatures
@app.before_request
def proxy_setup_and_db_router():
    """
    Handles upstream reverse-proxy headers (Nginx/Apache) 
    and hooks up the dynamic storage swapping routing rules.
    """
    # Safeguard for base URL generation inside proxies
    real_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    host_header = request.headers.get('X-Forwarded-Host', request.host)
    
    # Place your zstd compression and db size swap checks below:
    pass

@app.route('/')
@returns_rdf
def get_rdf_data():
    """
    Root endpoint serving basic RDF graph metadata via content negotiation.
    """
    graph = Graph()
    graph.add((URIRef("http://rdf/sparql.example.org"), FOAF.name, Literal("John Doe")))
    return graph

@app.route('/sparql', methods=['GET', 'POST'])
def sparql_endpoint():
    """
    Provides a query interface for processing semantic SPARQL lookups.
    """
    # Accept queries via GET parameters or raw POST bodies
    query_str = request.values.get('query') or request.get_data(as_text=True)
    
    if not query_str:
        return jsonify({"error": "No SPARQL query provided"}), 400
        
    try:
        results = semantic_store.query(query_str)
        # Check if the client requested JSON serialization or fallback to XML
        if "application/json" in request.headers.get("Accept", ""):
            return Response(results.serialize(format="json"), mimetype="application/json")
        return Response(results.serialize(format="xml"), mimetype="application/sparql-results+xml")
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/ontology.<fmt>')
def get_ontology(fmt):
    """
    Explicit route mapping for downloading static semantic graph files.
    Supports formats like: /ontology.ttl (Turtle), /ontology.owl, or /ontology.lemon
    """
    format_mapping = {
        'ttl': 'turtle',
        'owl': 'xml',
        'lemon': 'turtle'
    }
    
    rdf_format = format_mapping.get(fmt.lower())
    if not rdf_format:
        return "Unsupported format schema requested", 400
        
    # Serialize down matching the mapped file extension request
    output = semantic_store.serialize(format=rdf_format)
    return Response(output, mimetype=f"text/{rdf_format}" if fmt == 'ttl' else "application/rdf+xml")

# Main execution block for the server side
if __name__ == '__main__':
    app.run(
        host=os.environ.get('FLASK_RUN_HOST', '0.0.0.0'), 
        port=int(os.environ.get('FLASK_RUN_PORT', 5050)), 
        debug=True
    )
