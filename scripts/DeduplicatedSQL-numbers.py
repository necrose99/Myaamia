import sqlite3
import re

def setup_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # Lexicon: Unique Myaamia atoms
    cursor.execute("CREATE TABLE IF NOT EXISTS lexicon (id INTEGER PRIMARY KEY, term TEXT UNIQUE)")
    # Numbers: Mapping numeric values to sequences of lexicon IDs
    cursor.execute("CREATE TABLE IF NOT EXISTS numbers (id INTEGER PRIMARY KEY, val TEXT, pointers TEXT)")
    return conn, cursor

def clean_term(text):
    return text.replace('"', '').replace("'", "").strip()

def makišiweelo_sql(input_sql, output_db):
    conn, cursor = setup_db(output_db)
    lexicon = {}
    next_lex_id = 1
    
    # Regex to capture: id, numeric_val, myaamia_string
    pattern = re.compile(r"INSERT INTO word VALUES\((\d+),\s*'\"(.*?)\"',\s*'\"(.*?)\"'\);")

    with open(input_sql, 'r', encoding='utf-8') as f:
        for line in f:
            match = pattern.search(line)
            if not match:
                continue
                
            row_id, val, full
