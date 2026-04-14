#!/bin/python3 
##scripts/kilahkwaani.py

import json
import sqlite3
import sqlite-zstd
import re
import lxml.etree as ET
from pathlib import Path

# --- "Makišiweelo" Cultural Guardrails & G2P ---
gender_rules = {
    "iihia": "male", 
    "iiia": "male", 
    "naaka": "female"
}

def myaamia_to_ipa(text):
    mapping = [
        ('Å¡', 'š'), ('aa', 'aː'), ('ee', 'ɛː'), ('ii', 'iː'), ('oo', 'oː'),
        ('ay', 'aj'), ('aw', 'aw'), ('hk', 'ʰk'), ('ht', 'ʰt'), ('hp', 'ʰp'),
        ('hc', 'ʰtʃ'), ('š', 'ʃ'), ('č', 'tʃ'), ('c', 'tʃ')
    ]
    ipa = text.lower().strip('-')
    for orth, phon in mapping:
        ipa = ipa.replace(orth, phon)
    return f"/{ipa}/"

def get_voice_profile(myaamia_word):
    return gender_rules.get(myaamia_word.lower().strip('-'), "neutral")

# --- 2. Database Enrichment (TMX -> SQLite) ---
def enrich_from_tmx(db_path, tmx_file):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Ensure columns exist in the lexical_items table from your OLAC harvest
    try:
        cur.execute("ALTER TABLE lexical_items ADD COLUMN ipa TEXT")
        cur.execute("ALTER TABLE lexical_items ADD COLUMN ilda_id TEXT")
    except sqlite3.OperationalError:
        pass # Columns already exist

    print(f"[*] Enforcing TMX properties from {tmx_file}...")
    tree = ET.parse(tmx_file)
    
    for tu in tree.xpath("//tu"):
        ilda_id = tu.findtext(".//prop[@type='x-ilda-id']")
        myaamia_raw = tu.xpath(".//tuv[@xml:lang='mia']/seg")[0].text or ""
        myaamia_clean = myaamia_raw.replace('Å¡', 'š')
        ipa_val = myaamia_to_ipa(myaamia_clean)

        cur.execute('''
            UPDATE lexical_items 
            SET ipa = ?, ilda_id = ? 
            WHERE word = ? AND language_code = 'mia'
        ''', (ipa_val, ilda_id, myaamia_clean))

    conn.commit()
    conn.close()

# --- 3. Production Manifest Generation ---
def generate_web_manifest(db_path, output_json):
    manifest = {}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Pulling enriched data (including the new ilda_id and ipa)
    cur.execute("SELECT id, word, ipa, ilda_id FROM lexical_items WHERE language_code='mia'")
    
    for row in cur.fetchall():
        word = row['word']
        clean_key = word.strip('-').lower()
        
        manifest[clean_key] = {
            "id": row['id'],
            "ilda_id": row['ilda_id'],
            "orthography": word,
            "ipa": row['ipa'],
            "allophones": list(row['ipa'].strip('/')) if row['ipa'] else [],
            "voice_profile": get_voice_profile(clean_key),
            "has_recording": False,
            "sample_gender": "male"
        }

    with open(output_json, 'w', encoding='utf-8') as jf:
        json.dump(manifest, jf, indent=2, ensure_ascii=False)
    
    conn.close()
    print(f"[!] Makišiweelo! Web Manifest created at {output_json}")

if __name__ == "__main__":
    DB = 'data/olac_data.db'
    TMX = 'ilda_full.tmx'
    JSON_OUT = 'myaamia_assets.json'
    
    enrich_from_tmx(DB, TMX)
    generate_web_manifest(DB, JSON_OUT)
import json
import sqlite3
import os

# Cultural Guardrails
gender_rules = {
    "iihia": "male", 
    "iiia": "male", 
    "naaka": "female"
}

def init_tables(conn):
    """Generates SQLite tables if they do not exist."""
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS lexicon (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        term TEXT UNIQUE,
        ipa TEXT,
        voice_profile TEXT DEFAULT 'neutral'
    )''')
    conn.commit()

def get_voice_profile(word):
    clean = word.lower().strip('-')
    return gender_rules.get(clean, "neutral")

def generate_assets(db_path, output_json):
    conn = sqlite3.connect(db_path)
    init_tables(conn)
    cur = conn.cursor()

    # Step 1: Ensure existing terms have correct voice profiles
    cur.execute("SELECT id, term FROM lexicon")
    for row_id, term in cur.fetchall():
        profile = get_voice_profile(term)
        cur.execute("UPDATE lexicon SET voice_profile = ? WHERE id = ?", (profile, row_id))
    conn.commit()

    # Step 2: Build the JS-ready manifest
    manifest = {}
    cur.execute("SELECT term, ipa, voice_profile FROM lexicon")
    for term, ipa, profile in cur.fetchall():
        manifest[term.lower()] = {
            "orthography": term,
            "ipa": ipa or "",
            "voice": profile,
            "type": "gendered" if profile != "neutral" else "standard"
        }

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    conn.close()

if __name__ == "__main__":
    generate_assets('myaamia_relational.db', 'kilahkwaani_assets.json')
