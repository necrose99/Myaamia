# helpers/sounder-plug.py
import os
import json
import sqlite3
import uuid

HELPERS_DIR = os.path.abspath(os.path.dirname(__file__))

def init_audio_columns(conn):
    """Dynamically extends the core entries schema to track media metadata blocks."""
    cur = conn.cursor()
    # Add advanced audio profiling structures if missing from base setup
    alterations = [
        "ALTER TABLE entries ADD COLUMN audio_url TEXT",
        "ALTER TABLE entries ADD COLUMN wav2vec_tokens TEXT",
        "ALTER TABLE entries ADD COLUMN intonation_tags TEXT",
        "ALTER TABLE entries ADD COLUMN voice_gender TEXT"
    ]
    for statement in alterations:
        try:
            cur.execute(statement)
        except sqlite3.OperationalError:
            pass # Columns already provisioned in database schema
    conn.commit()

def transmog_process(file_bytes: bytes, src_lang: str, db_path: str) -> dict:
    """
    Standard plugin hook entry point. Parses preprocessed audio jsonl records
    (Wav2Vec segments, phonetic tones, and audio hosting parameters) into SQLite rows.
    """
    conn = sqlite3.connect(db_path)
    init_audio_columns(conn)
    cur = conn.cursor()
    
    # Process string content straight out of memory-buffers
    data_stream = file_bytes.decode('utf-8', errors='ignore')
    seen_count = 0
    updated_count = 0
    
    for line in data_stream.splitlines():
        if not line.strip(): 
            continue
        try:
            item = json.loads(line)
            seen_count += 1
            
            # Map parameters from jsonl models (e.g., wav2vec outputs or admin maps)
            form = item.get("word") or item.get("orthography") or item.get("form")
            if not form: 
                continue
                
            ipa_val = item.get("ipa") or ""
            audio_url = item.get("audio_url") or item.get("mp3_url") or ""
            wav2vec = json.dumps(item.get("wav2vec_data") or item.get("tokens") or [])
            intonation = item.get("intonation") or item.get("pitch_pattern") or ""
            gender = item.get("voice_gender") or item.get("gender") or "neutral"
            
            # Update matching entries based on standard lookup forms
            cur.execute("""
                UPDATE entries 
                SET ipa = COALESCE(NULLIF(?, ''), ipa),
                    audio_url = COALESCE(NULLIF(?, ''), audio_url),
                    wav2vec_tokens = NULLIF(?, '[]'),
                    intonation_tags = COALESCE(NULLIF(?, ''), intonation_tags),
                    voice_gender = ?
                WHERE form = ? AND lang = ?
            """, (ipa_val, audio_url, wav2vec, intonation, gender, form, src_lang))
            
            if cur.rowcount > 0:
                updated_count += 1
                
        except json.JSONDecodeError:
            continue
            
    conn.commit()
    conn.close()
    
    # Force auto-regeneration of your client asset manifest mapping targets
    try:
        import kilahkwaani
        # Re-compile static/kilahkwaani_assets.json behind the scenes
        kilahkwaani.generate_kilahkwaani_manifest(db_path, "static/kilahkwaani_assets.json")
    except ImportError:
        pass

    return {
        "status": "success",
        "plugin": "sounder-plug",
        "jsonl_lines_read": seen_count,
        "database_rows_enriched": updated_count
    }
