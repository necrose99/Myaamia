#!/usr/bin/python3
import sqlite3
import requests
import struct
import time
import sys

# Configuration
DB_PATH = "algic_rag.db"
OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL_NAME = "bge-m3" # Ensure you ran 'ollama pull bge-m3'
BATCH_SIZE = 50       # Number of rows to process per commit

def serialize_f32(vector):
    """Convert a list of floats to a BLOB for sqlite-vec."""
    return struct.pack(f"{len(vector)}f", *vector)

def get_embedding(text):
    """Fetch 1024-dimensional embedding from local Ollama."""
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "input": text
        }, timeout=30)
        response.raise_for_status()
        # BGE-M3 returns a list of embeddings; we take the first for the input string
        return response.json()["embeddings"][0]
    except Exception as e:
        print(f"\n[!] Ollama Error: {e}")
        return None

def vectorize_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # We only target languages with text but NO existing vector
    # Prioritizing Miami-Illinois (mia) first
    targets = ['mia', 'sac', 'kic', 'sha', 'cre', 'oji']
    
    print(f"[*] Starting Vectorization Factory (Model: {MODEL_NAME})")

    for lang in targets:
        text_col = f"{lang}_text"
        vec_col = f"{lang}_vector"
        
        # Count pending rows
        cur.execute(f"SELECT COUNT(*) FROM TranslationUnits WHERE {text_col} IS NOT NULL AND {vec_col} IS NULL")
        pending = cur.fetchone()[0]
        
        if pending == 0:
            print(f"[-] No pending work for {lang.upper()}")
            continue

        print(f"[*] Processing {pending} rows for {lang.upper()}...")
        
        cur.execute(f"SELECT id, {text_col} FROM TranslationUnits WHERE {text_col} IS NOT NULL AND {vec_col} IS NULL")
        rows = cur.fetchall()

        processed = 0
        for row_id, text in rows:
            vector = get_embedding(text)
            if vector:
                serialized = serialize_f32(vector)
                cur.execute(f"UPDATE TranslationUnits SET {vec_col} = ? WHERE id = ?", (serialized, row_id))
                processed += 1
                
                # Progress bar for the terminal
                sys.stdout.write(f"\r  Progress: [{processed}/{pending}]")
                sys.stdout.flush()

                if processed % BATCH_SIZE == 0:
                    conn.commit()

        conn.commit()
        print(f"\n[+] {lang.upper()} Vectorization Complete.")

    conn.close()

if __name__ == "__main__":
    vectorize_database()
