#!/usr/bin/python3
##### tmx2sqlite.py generate basic sqlite db
import sqlite3
import datetime
import argparse
import sys
from glob import glob
from xml.etree.ElementTree import iterparse

# Comprehensive Algic Language List from your provided stack
ALGIC_LANGS = [
    'bft', 'arp', 'ats', 'chy', 'men', 'cre', 'csw', 'crj', 'atj', 
    'pot', 'oji', 'otw', 'ciw', 'mia', 'sac', 'kic', 'sha', 
    'mic', 'abe', 'aaq', 'mal', 'moo', 'mua', 'unm', 'alg_x_proto', 'en'
]

def setup_rag_db(db_path, drop_tables=False):
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    if drop_tables:
        cur.execute("DROP TABLE IF EXISTS TranslationUnits")
        cur.execute("DROP TABLE IF EXISTS TmxImportFiles")

    # Create Import Tracking
    cur.execute("""
        CREATE TABLE IF NOT EXISTS TmxImportFiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            tmxfile TEXT, 
            started TEXT, 
            completed TEXT
        )
    """)

    # Build Dynamic SQL for Translation Units
    # Every language gets a text column AND a vector (embedding) column
    cols = ["id INTEGER PRIMARY KEY AUTOINCREMENT", "orig_tuid TEXT", "import_id INT"]
    for lang in ALGIC_LANGS:
        cols.append(f"{lang}_text TEXT")
        cols.append(f"{lang}_vector BLOB") # For sqlite-vec embeddings
    
    create_statement = f"CREATE TABLE IF NOT EXISTS TranslationUnits ({', '.join(cols)})"
    cur.execute(create_statement)
    return con

def insert_tus(db_con, nodes, import_id):
    cur = db_con.cursor()
    count = 0
    
    # Prepare Insert Statement
    columns = ["orig_tuid", "import_id"] + [f"{l}_text" for l in ALGIC_LANGS]
    placeholders = ", ".join(["?"] * len(columns))
    sql = f"INSERT INTO TranslationUnits ({', '.join(columns)}) VALUES ({placeholders})"

    try:
        for event, node in nodes:
            if event == 'end' and node.tag == 'tu':
                row_data = {f"{l}_text": None for l in ALGIC_LANGS}
                row_data["orig_tuid"] = node.attrib.get('tuid', '0')
                row_data["import_id"] = import_id

                for tuv in node.findall('tuv'):
                    # Handle namespaces and normalize lang codes
                    lang_attr = tuv.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'en')
                    lang_key = lang_attr.split('-')[0].lower().replace('-', '_')
                    
                    seg = tuv.find('seg')
                    if seg is not None and seg.text and lang_key in ALGIC_LANGS:
                        row_data[f"{lang_key}_text"] = seg.text

                # Execute Insert
                val_tuple = (row_data["orig_tuid"], row_data["import_id"]) + \
                            tuple(row_data[f"{l}_text"] for l in ALGIC_LANGS)
                cur.execute(sql, val_tuple)
                
                count += 1
                node.clear() # Memory management for large files
                
                if count % 500 == 0:
                    db_con.commit()
    except Exception as e:
        print(f"Error during TU insertion: {e}")
    
    return count

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Algic RAG TMX to SQLite Importer")
    parser.add_argument('--drop', action='store_true', help='Drop existing tables')
    parser.add_argument('--db', default='algic_rag.sqlite', help='Database name')
    parser.add_argument(dest='infiles', nargs='+', help='TMX files to import')
    args = parser.parse_args()

    con = setup_rag_db(args.db, args.drop)
    
    for pattern in args.infiles:
        for tmx_file in glob(pattern):
            print(f"[*] Importing: {tmx_file}")
            start_time = datetime.datetime.now()
            
            cur = con.cursor()
            cur.execute("INSERT INTO TmxImportFiles(tmxfile, started) VALUES(?, ?)", (tmx_file, str(start_time)))
            import_id = cur.lastrowid

            # Parse XML
            nodes = iter(iterparse(tmx_file, events=['start', 'end']))
            _, root = next(nodes) # Skip root
            
            inserted = insert_tus(con, nodes, import_id)
            
            end_time = datetime.datetime.now()
            cur.execute("UPDATE TmxImportFiles SET completed = ? WHERE id = ?", (str(end_time), import_id))
            con.commit()
            print(f"[+] Finished. Inserted {inserted} records in {end_time - start_time}")

    con.close()
