# helpers/ollama_plugin.py
import sqlite3
import httpx
import json
import os
from typing import Dict, Any, List, Optional

# Core etymology graph & sqlite mapping tools
import ety
import sqlite_utils
from llm.plugins import load_plugins

class AlgicOllamaPlugin:
    def __init__(self, db_path: str, model_name: str = "hermes3", embedding_model: str = "nomic-embed-text"):
        self.db_path = db_path
        self.model = model_name
        self.embedding_model = embedding_model
        self.ollama_base_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        
        # Initialize extension hooks for llm-sqlite tracking if needed
        self._ensure_vector_workspace()

    def _ensure_vector_workspace(self):
        """
        Ensures llm-sqlite vector workspace metadata and schema tables 
        exist natively inside the target database without corrupting core rows.
        """
        db = sqlite_utils.Database(self.db_path)
        # Setup vector embedding collection tables if not initialized by LLM CLI
        if "embeddings" not in db.table_names():
            db["embeddings"].create({
                "collection": str,
                "id": str,
                "embedding": bytes
            }, pk=("collection", "id"))

    def compute_local_embedding(self, text: str) -> List[float]:
        """Queries local Ollama instance to generate vector slices for NLS semantic matching."""
        try:
            res = httpx.post(
                f"{self.ollama_base_url}/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
                timeout=10.0
            )
            if res.status_code == 200:
                return res.json().get("embedding", [])
            return []
        except Exception:
            return []

    def get_etymology_graph_data(self, word_form: str) -> Dict[str, Any]:
        """
        Uses the internal 'ety' library to trace structural cognates 
        and format them as standard visualization nodes/edges.
        """
        try:
            origins = ety.origins(word_form)
            nodes = [{"id": word_form, "label": word_form, "type": "origin"}]
            edges = []
            
            for index, parent in enumerate(origins):
                node_id = f"{parent.text}_{index}"
                nodes.append({"id": node_id, "label": f"{parent.language.name}: {parent.text}", "type": "ancestor"})
                edges.append({"source": node_id, "target": word_form, "relationship": "derived"})
            return {"nodes": nodes, "edges": edges}
        except Exception as e:
            return {"error": f"Graph computation error: {str(e)}", "nodes": [], "edges": []}

    def generate_rag_insight(self, entry_id: str) -> Dict[str, Any]:
        """
        Pipes direct SQLite rows, vector match candidates, and structural 
        graph configurations down to Hermes 3 for language analysis.
        """
        # 1. Fetch source lexical item metadata
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            entry = cursor.execute(
                "SELECT form, lang, gloss_en, ipa, proto_form FROM entries WHERE id = ?", 
                (entry_id,)
            ).fetchone()
            
        if not entry:
            return {"error": "Target etymology entry index not found in database"}

        entry_data = dict(entry)
        
        # 2. Extract etymological topology tree data
        graph_tree = self.get_etymology_graph_data(entry_data["form"])
        
        # 3. Construct Context Payload for Hermes 3 tool-calling loop
        system_prompt = (
            "You are an expert computational linguist evaluating Algic languages. "
            "Examine the phonetic IPA shifts, semantic definitions, and derivation trees. "
            "Output your entire analysis strictly as a single JSON object."
        )
        
        user_prompt = f"""
        Analyze Word: '{entry_data['form']}' [{entry_data['lang']}]
        Phonetic IPA: {entry_data['ipa'] or 'Unknown'}
        English Gloss: {entry_data['gloss_en']}
        Claimed Proto-Form: {entry_data['proto_form'] or 'None'}
        
        Contextual Etymology Subgraph Data:
        {json.dumps(graph_tree)}
        
        Task:
        - Validate if phonetic structure conforms to Algic or Proto-Algonquian sound laws.
        - Provide structural layout markers (initials, medials, finals) if compound.
        - Note potential semantic shifts based on ancestral graphs.
        """

        try:
            res = httpx.post(
                f"{self.ollama_base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "options": {"temperature": 0.2},
                    "stream": False,
                    "format": "json"
                },
                timeout=45.0
            )
            if res.status_code == 200:
                content = res.json().get("message", {}).get("content", "{}")
                return json.loads(content)
            return {"error": f"Ollama service error: HTTP {res.status_code}"}
        except Exception as e:
            return {"error": f"Failed compiling AI insights: {str(e)}"}
