#!/usr/bin/env python3
"""
algic_ety_applet_v3.py — Algic Etymology Applet (Integrated with Kilahkwaani v2)
Symlinked directly to app.py running on port 5000.
Passes semantic triple streams dynamically down to port 5050.
"""
from __future__ import annotations
import os
import sys
import requests
from flask import Flask, jsonify, request, render_template, g, Response

# 1. Register background plugin environment boundaries
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "helpers"))

import plugins
from Admin import cfg
from helpers.db_factory import init_databases, db_sql, whooshee
from helpers.kilahkwaani import build_speech_manifest

# Extension Packages Integration Array
from flask_babel import Babel, gettext as _
from flask_bootstrap import Bootstrap5
from flask_argon2 import Argon2
from flask_wiki import Wiki

# Initialize core decoupling variables
SPARQL_BACKEND_URL = os.environ.get("SPARQL_BACKEND_URL", "http://127.0.0.1:5050")

def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    
    # Cascade configuration options from Admin module
    app.config.from_object(cfg)
    app.config.setdefault("SECRET_KEY", getattr(cfg, "SECRET_KEY", "fallback-secret-key-321"))
    app.config.setdefault("DB_TYPE", "sqlite")
    app.config.setdefault("USE_REDIS", True)
    app.config.setdefault("SQLITE_DB_PATH", os.getenv("DB_PATH", "data/olac_data.db"))
    app.config["WIKI_TEMPLATE"] = "wiki_custom.html"

    # Boot database extensions and search structures 
    wrangler = init_databases(app)
    whooshee.init_app(app)
    Bootstrap5(app)
    Argon2(app)
    
    # Initialize interactive developer log documentation wiki 
    wiki = Wiki()
    wiki.init_app(app)

    # Initialize localization context switching layer
    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        """Automatically reads language requests out of user browser sessions"""
        return request.accept_languages.best_match(['en', 'fr', 'es', 'mia'])

    @app.before_request
    def set_global_lang():
        g.lang_code = get_locale()

    # Create relational persistence storage layout mapping
    with app.app_context():
        if app.config["DB_TYPE"] == "sqlite":
            db_sql.create_all()

    # ── Operational Endpoint Routes ───────────────────────────────────────────

    @app.route("/")
    def index():
        """Serves dynamic Kilahkwaani core template with translation bindings."""
        try:
            # Re-issue background call down to Port 5050 to fetch fresh Turtle headers
            res = requests.get(f"{SPARQL_BACKEND_URL}/", headers={"Accept": "text/turtle"}, timeout=2)
            turtle_preview = res.text
        except Exception:
            turtle_preview = _("# Port 5050 Triplestore offline. Displaying template local context.")
            
        return render_template("index.html", turtle_preview=turtle_preview)

    @app.route("/api/speech-manifest", methods=["GET"])
    def speech_manifest():
        """Serves the speech dictionary metadata arrays out to browser kilahkwaani_v2.js."""
        manifest = build_speech_manifest(wrangler)
        return jsonify(manifest)

    @app.route("/admin/import/universal", methods=["POST"])
    def admin_import_universal():
        """Universal ingestion pipeline parsing XSLT via background helper plugins."""
        file = request.files.get("file")
        fmt = request.form.get("format")       # e.g., 'extended-tmx', 'xdxf'
        lang = request.form.get("lang", "mia")
        
        if not file or not fmt:
            return jsonify({"error": _("Missing input file stream or format signature identifier")}), 400
            
        try:
            xslt_dir = os.path.join(app.root_path, "xslt")
            db_path = app.config["SQLITE_DB_PATH"]
            manager = plugins.PluginManager(db_path, xslt_dir)
            result = manager.process_universal_import(fmt, file.read(), lang)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/sparql', methods=['GET', 'POST'])
    @app.route('/rdf/<path:url_path>', methods=['GET', 'POST'])
    def semantic_passthrough_proxy(url_path=""):
        """
        Pipes request payload queries seamlessly between UI Port 5000 
        and the semantic RDF store engine processing instructions on Port 5050.
        """
        sub_path = f"/rdf/{url_path}" if url_path else "/sparql" if "sparql" in request.path else "/"
        target_url = f"{SPARQL_BACKEND_URL}{sub_path}"
        
        try:
            backend_res = requests.request(
                method=request.method,
                url=target_url,
                headers={k: v for k, v in request.headers if k.lower() != 'host'},
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False,
                params=request.args
            )
            return Response(backend_res.content, status=backend_res.status_code, headers=dict(backend_res.headers))
        except Exception as e:
            return jsonify({"error": f"Port 5050 Backend unreachable: {str(e)}"}), 502

    return app

if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)
