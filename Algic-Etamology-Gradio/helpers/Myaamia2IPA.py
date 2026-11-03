import re
import sqlite3
import lxml.etree as ET
from xml.sax.saxutils import escape

# --- 1. Myaamia Grapheme-to-Phoneme (G2P) ---
def myaamia_to_ipa(text):
    """Converts Myaamia orthography to IPA allophones."""
    # Order: clusters/long vowels first to prevent partial replacement
    mapping = [
        ('Å¡', 'š'), ('aa', 'aː'), ('ee', 'ɛː'), ('ii', 'iː'), ('oo', 'oː'),
        ('ay', 'aj'), ('aw', 'aw'), 
        ('hk', 'ʰk'), ('ht', 'ʰt'), ('hp', 'ʰp'), ('hc', 'ʰtʃ'),
        ('š', 'ʃ'), ('č', 'tʃ'), ('c', 'tʃ')
    ]
    
    ipa = text.lower().strip('-')
    for orth, phon in mapping:
        ipa = ipa.replace(orth, phon)
    return f"/{ipa}/"

# --- 2. Database Initialization (The Pointer System) ---
def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Lexicon stores the atoms/roots
    cur.execute("CREATE TABLE IF NOT EXISTS lexicon (id INTEGER PRIMARY KEY, term TEXT UNIQUE, ipa TEXT)")
    # Numbers stores the numeric sequence pointers
    cur.execute("CREATE TABLE IF NOT EXISTS numbers (id INTEGER PRIMARY KEY, val TEXT, pointers TEXT)")
    conn.commit()
    return conn

# --- 3. The Main Pipeline ---
def makishiweelo_pipeline(tmx_file, sql_file, db_out, pot_out):
    conn = init_db(db_out)
    cur = conn.cursor()
    
    # A. Process TMX to populate Lexicon
    print(f"[*] Processing {tmx_file}...")
    tree = ET.parse(tmx_file)
    lex_map = {} # term -> id mapping for sql step
    
    with open(pot_out, 'w', encoding='utf-8') as pot:
        pot.write('msgid ""\nmsgstr ""\n"Project-Id-Version: Myaamia-Relational\\n"\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n')
        
        for tu in tree.xpath("//tu"):
            ilda_id = tu.findtext(".//prop[@type='x-ilda-id']")
            # Fix common TMX encoding artifacts in the Myaamia segment
            myaamia_raw = tu.xpath(".//tuv[@xml:lang='mia']/seg")[0].text or ""
            myaamia_clean = myaamia_raw.replace('Å¡', 'š')
            english = tu.xpath(".//tuv[@xml:lang='en-US']/seg")[0].text or ""
            
            ipa_val = myaamia_to_ipa(myaamia_clean)
            
            # Update SQLite Lexicon
            cur.execute("INSERT OR IGNORE INTO lexicon (term, ipa) VALUES (?, ?)", (myaamia_clean, ipa_val))
            cur.execute("SELECT id FROM lexicon WHERE term=?", (myaamia_clean,))
            lex_id = cur.fetchone()[0]
            lex_map[myaamia_clean] = lex_id
            
            # Write to POT with [$ipa] note
            pot.write(f"#. ID: {ilda_id}\n#. [$ipa]: {ipa_val}\n")
            pot.write(f'msgid "{english}"\nmsgstr "{myaamia_clean}"\n\n')

    # B. Process numbers.sql to populate Numbers table with Pointers
    print(f"[*] Processing {sql_file}...")
    # Matches: INSERT INTO word VALUES(id, '"value"', '"myaamia"');
    insert_pattern = re.compile(r"INSERT INTO word VALUES\((\d+),\s*'\"(.*?)\"',\s*'\"(.*?)\"'\);")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = insert_pattern.search(line)
            if match:
                row_id, val, full_text = match.groups()
                tokens = full_text.split()
                ptr_list = []
                
                for t in tokens:
                    t = t.replace('"', '').strip()
                    if not t: continue
                    # Check lexicon, add if missing (unlikely if TMX is full)
                    if t not in lex_map:
                        cur.execute("INSERT OR IGNORE INTO lexicon (term, ipa) VALUES (?, ?)", (t, myaamia_to_ipa(t)))
                        cur.execute("SELECT id FROM lexicon WHERE term=?", (t,))
                        lex_map[t] = cur.fetchone()[0]
                    ptr_list.append(str(lex_map[t]))
                
                cur.execute("INSERT INTO numbers (id, val, pointers) VALUES (?, ?, ?)", 
                            (row_id, val, ",".join(ptr_list)))

    conn.commit()
    conn.close()
    print(f"[!] Success: Database '{db_out}' and POT '{pot_out}' created.")

# --- Execution ---
if __name__ == "__main__":
    # Ensure filenames match your uploads
    makishiweelo_pipeline('ilda_full.tmx', 'numbers.sql', 'myaamia_relational.db', 'myaamia_allophones.pot')
