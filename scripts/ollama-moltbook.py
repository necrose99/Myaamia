import os
import json
import sqlite_vec
import sqlite3
import requests
import wandb
from ollama import Client

# Configuration
MOLTBOOK_API = "https://www.moltbook.com/api/v1"
AGENT_TOKEN = os.getenv("MOLTBOOK_TOKEN")
DB_PATH = "algic_linguistics.db"
MODEL_NAME = "mistral-openorca" # Or your fine-tuned Algic model

# Initialize WandB for SKILL0 tracking
wandb.init(project="moltbook-algic-agent", job_type="skill-execution")

# Initialize Ollama Client
client = Client(host='http://localhost:11434')

def setup_db():
    """Initializes SQLite with vector support for IPA/Etymology storage."""
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    
    # Example Table for Algic Language Pairs (TMX style)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY,
            lang_code TEXT, -- e.g., 'crj', 'bft'
            original_text TEXT,
            ipa_notation TEXT,
            embedding_v FLOAT[1536] -- Vector for RAG
        )
    """)
    return conn

def get_rag_context(query_text):
    """Uses llm-tools-sqlite logic to find relevant linguistic context."""
    # Simplified: in practice, use 'llm embed' to generate query vector
    return "Context: In Southern East Cree (crj), allophones often vary based on vowel proximity."

def post_to_moltbook(content, submolt="m/linguistics"):
    """Posts insights to Moltbook."""
    headers = {"Authorization": f"Bearer {AGENT_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "content": content,
        "submolt": submolt,
        "tags": ["Algic", "RAG", "IPA"]
    }
    res = requests.post(f"{MOLTBOOK_API}/posts", headers=headers, json=payload)
    return res.json()

def run_agent_cycle():
    # 1. Retrieve data from local SQLite (RAG)
    context = get_rag_context("Explain allophones in Algic languages")
    
    # 2. Query Ollama
    prompt = f"{context}\n\nUser: Create a post for m/linguistics about Cheyenne (chy) phonology."
    response = client.generate(model=MODEL_NAME, prompt=prompt)
    
    # 3. Post to Moltbook
    molt_response = post_to_moltbook(response['response'])
    
    # 4. Log to WandB
    wandb.log({"post_status": "success", "content_length": len(response['response'])})
    print(f"Agent Posted: {molt_response}")

if __name__ == "__main__":
    setup_db()
    run_agent_cycle()
import os
import sqlite3
import sqlite_vec
import requests
from ollama import Client

# Initialize SQLite-vec
db = sqlite3.connect("db/algic_linguistics.db")
db.enable_load_extension(True)
sqlite_vec.load(db)

# Moltbook Registration Helper (as per skill.md)
def register_agent():
    if not os.getenv("MOLTBOOK_API_KEY"):
        res = requests.post("https://www.moltbook.com/api/v1/agents/register", 
                            json={"name": "AlgicAgent_v1", "description": "Linguistic RAG Agent"})
        print(f"SAVE THIS KEY: {res.json().get('api_key')}")
        # Follow the Claim URL in the response to activate!

def post_discovery(content, submolt="m/linguistics"):
    headers = {"Authorization": f"Bearer {os.getenv('MOLTBOOK_API_KEY')}"}
    payload = {"submolt": submolt, "title": "New Algic Linguistic Insight", "content": content}
    requests.post("https://www.moltbook.com/api/v1/posts", json=payload, headers=headers)

# Main Loop: Check Voyager output -> Post to Moltbook
if __name__ == "__main__":
    register_agent()
    # Logic to query your SQLite-vec for new allophone/TMX data goes here
