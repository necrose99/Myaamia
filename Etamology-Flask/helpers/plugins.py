# helpers/plugins.py
import os
import sys
import importlib
import logging
from typing import Dict, Any, List
from flask import Blueprint, Flask

try:
    from ollama_plugin import AlgicOllamaPlugin
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

class PluginManager:
    def __init__(self, db_path: str, xslt_dir: str, enable_ai: bool = True):
        self.db_path = db_path
        self.xslt_dir = xslt_dir
        self.loaded_features: Dict[str, Any] = {}
        
        # 1. Initialize core AI processing module
        self.ai_enabled = enable_ai and OLLAMA_AVAILABLE
        if self.ai_enabled:
            self.ai_agent = AlgicOllamaPlugin(db_path=db_path)
            self.loaded_features["ollama"] = self.ai_agent
        else:
            self.ai_agent = None
            logging.warning("Ollama plugin hook initialization bypassed.")

        # 2. Establish dynamic file system discovery loop
        self._discover_and_load_addons()

    def _discover_and_load_addons(self):
        """
        Scans helpers directory for files ending in '-plugin.py' or '_plugin.py'
        and dynamically instantiates them into the engine runtime context.
        """
        helpers_dir = os.path.dirname(os.path.abspath(__file__))
        if helpers_dir not in sys.path:
            sys.path.insert(0, helpers_dir)

        for filename in os.listdir(helpers_dir):
            if (filename.endswith("_plugin.py") or filename.endswith("-plugin.py")) and filename != "ollama_plugin.py":
                module_name = filename.rsplit(".", 1)[0].replace("-", "_")
                try:
                    # Dynamic runtime import loop
                    mod = importlib.import_module(module_name)
                    
                    # Look for a standard initialization hook within the target module
                    if hasattr(mod, "initialize_plugin"):
                        plugin_instance = mod.initialize_plugin(self.db_path, self.xslt_dir)
                        self.loaded_features[module_name] = plugin_instance
                        logging.info(f"Successfully mounted addon architecture: {module_name}")
                except Exception as e:
                    logging.error(f"Failed loading runtime module hook [{module_name}]: {str(e)}")

    def mount_blueprints_to_app(self, app: Flask):
        """
        Discovers any Flask Blueprints declared inside custom plugin engines 
        and registers them directly into the primary application context.
        """
        for feature_name, feature_instance in self.loaded_features.items():
            if hasattr(feature_instance, "blueprint") and isinstance(feature_instance.blueprint, Blueprint):
                app.register_blueprint(feature_instance.blueprint)
                logging.info(f"Registered routing injection matrix from: {feature_name}")

    def execute_sandbox_discovery(self, query_string: str) -> dict:
        """Screening Gate: Runs isolated auto-discovery queries against semantic sets."""
        clean_sql = query_string.strip()
        destructive_keywords = ["drop", "truncate", "alter", "grant", "revoke", "vacuum"]
        if any(kw in clean_sql.lower() for kw in destructive_keywords):
            raise PermissionError("Unsafe structural operation intercepted by plugin gate.")
            
        allowed_scopes = ["embeddings", "tmx_clones", "rdf_triples", "ipa_phonetics"]
        if not any(table in clean_sql.lower() for table in allowed_scopes):
            raise PermissionError("Access Denied: LLM query targeted raw primary data fields.")

        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(clean_sql)
            conn.commit()
            return {"status": "success", "rows_affected": cursor.rowcount}
