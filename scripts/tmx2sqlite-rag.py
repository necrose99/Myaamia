#!/usr/bin/python3
import sqlite3
import datetime
import argparse
import sys
import os
from glob import glob
from xml.etree.ElementTree import iterparse

# Genetic distance weights relative to Miami-Illinois
# Used to boost search results in the RAG interface
LANG_PRIORITY = {
    'mia': 1.0,  # Miami-Illinois (Primary)
    'sac': 0.8,  # Meskwaki (Cousin)
    'kic': 0.8,  # Kickapoo (Cousin)
    'sha': 0.8,  # Shawnee (Cousin)
    'cre': 0.5,  # Cree (Central)
    'oji': 0.5,  # Ojibwe (Central)
    'en': 0.1    # English (Reference)
}

def setup_database(db_path, drop=False):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if drop:
        cursor.execute("DROP TABLE IF EXISTS TranslationUnits")
        cursor.execute("DROP TABLE IF EXISTS TmxFiles")

    # Tracking Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TmxFiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            timestamp TEXT
        )
    """)

    # RAG Table: Dynamic columns based on your language stack
    # Each language gets: [lang]_text and [lang]_vector
    columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT", "orig_tuid TEXT", "import_id INTEGER", "priority_weight REAL"]
    for lang in LANG_PRIORITY.keys():
        columns.append(f"{lang}_text TEXT")
        columns.append(f"{lang}_vector BLOB") # Reserved for sqlite-vec

    cursor.execute(f"CREATE TABLE IF NOT EXISTS TranslationUnits ({', '.join(columns)})")
    return conn

def process_tmx(conn, tmx_path, import_id):
    cursor = conn.cursor()
    count = 0
    
    # Prepare the INSERT statement dynamically
    langs = list(LANG_PRIORITY.keys())
    col_names = ["orig_tuid", "import_id", "priority_weight"] + [f"{l}_text" for l in langs]
    placeholders = ", ".join(["?"] * len(col_names))
    insert_sql = f"INSERT INTO TranslationUnits ({', '.join(col_names)}) VALUES ({placeholders})"

    # Iterparse handles large files without RAM bloating
    context = iterparse(tmx_path, events=('start', 'end'))
    event, root = next(context) 

    for event, elem in context:
        if event == 'end' and elem.tag == 'tu':
            row = {l: None for l in langs}
            tuid = elem.attrib.get('tuid', '0')
            max_weight = 0.1

            for tuv in elem.findall('tuv'):
                lang_raw = tuv.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'en')
                lang_code = lang_raw.split('-')[0].lower()
                
                seg = tuv.find('seg')
                if seg is not None and seg.text and lang_code in row:
                    row[lang_code] = seg.text
                    # Track the highest priority language present in this TU
                    max_weight = max(max_weight, LANG_PRIORITY.get(lang_code, 0.1))

            # Execute Insert
            values = [tuid, import_id, max_weight] + [row[l] for l in langs]
            cursor.execute(insert_sql, values)
            
            count += 1
            root.clear() # Clear memory
            if count % 1000 == 0:
                conn.commit()
                print(f"  Processed {count} units...", end='\r')
                
    conn.commit()
    return count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Algic TMX to RAG-SQLite Pipeline")
    parser.add_argument('files', nargs='+', help="TMX files or glob patterns")
    parser.add_argument('--db', default='algic_rag.db', help="Database output path")
    parser.add_argument('--drop', action='store_true', help="Drop existing tables before import")
    args = parser.parse_args()

    db_conn = setup_database(args.db, args.drop)
    total = 0

    for pattern in args.files:
        for file_path in glob(pattern):
            print(f"[*] Importing {os.path.basename(file_path)}...")
            
            # Log the import
            cur = db_conn.cursor()
            cur.execute("INSERT INTO TmxFiles (filename, timestamp) VALUES (?, ?)", 
                        (file_path, datetime.datetime.now().isoformat()))
            imp_id = cur.lastrowid
            
            added = process_tmx(db_conn, file_path, imp_id)
            total += added
            print(f"\n[+] Success: {added} units added.")

    db_conn.close()
    print(f"\n--- Import Complete. Total Records: {total} ---")

