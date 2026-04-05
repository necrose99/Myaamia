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
