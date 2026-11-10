#!/usr/bin/env python3
import sqlite3

# --- 1. Core Lexemes from your TMX Builder Data ---
ONES = {
    1: "nkoti", 2: "niišwi", 3: "nihswi", 4: "niiwi", 
    5: "yaalanwi", 6: "kaakaathswi", 7: "swaahteethswi", 
    8: "palaani", 9: "nkotimeneehki"
}

TENS = {
    2: "niišwi mateeni", 3: "nihswi mateeni", 4: "niiwi mateeni",
    5: "yaalanwi mateeni", 6: "kaakaathswi mateeni", 7: "swaahteethswi mateeni",
    8: "palaani mateeni", 9: "nkotimeneehki mateeni"
}

HUNDREDS = {
    1: "nkotwaahkwe", 2: "niišwaahkwe", 3: "nihswaahkwe", 4: "niiwaahkwe",
    5: "yaalanwaahkwe", 6: "kaakaathswaahkwe", 7: "swaahteethswaahkwe",
    8: "palaanwaahkwe", 9: "nkotimeneehkwaahkwe"
}

THOUSANDS = {
    1: "mataathswaahkwe",  # Modern
    1000: "mittahsoak",    # Archival
    10000: "kiciouae"      # Archival
}

RULES = {
    "teen_prefix": "mataathswi",
    "teen_suffix": "aasi"
}

# --- 2. Database Execution & Schema Index Staging ---
def build_myaamia_search_index(db_path="myaamia_lexicon.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Core structural tables
    cursor.execute("DROP TABLE IF EXISTS raw_lexemes;")
    cursor.execute("""
    CREATE TABLE raw_lexemes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numeric_value INTEGER,
        surface_form TEXT,
        category TEXT -- 'ONE', 'TEN_BASE', 'HUNDRED', 'THOUSAND', 'PARTICLE'
    );
    """)

    # Populate atomic pieces
    for val, term in ONES.items():
        cursor.execute("INSERT INTO raw_lexemes (numeric_value, surface_form, category) VALUES (?, ?, 'ONE')", (val, term))
    for val, term in TENS.items():
        cursor.execute("INSERT INTO raw_lexemes (numeric_value, surface_form, category) VALUES (?, ?, 'TEN_BASE')", (val * 10, term))
    for val, term in HUNDREDS.items():
        cursor.execute("INSERT INTO raw_lexemes (numeric_value, surface_form, category) VALUES (?, ?, 'HUNDRED')", (val * 100, term))
    
    # Archival vs Modern Thousand flags
    cursor.execute("INSERT INTO raw_lexemes (numeric_value, surface_form, category) VALUES (1000, ?, 'THOUSAND')", (THOUSANDS[1],))
    cursor.execute("INSERT INTO raw_lexemes (numeric_value, surface_form, category) VALUES (1000, ?, 'THOUSAND_ARCHIVAL')", (THOUSANDS[1000],))
    cursor.execute("INSERT INTO raw_lexemes (numeric_value, surface_form, category) VALUES (10000, ?, 'THOUSAND_ARCHIVAL')", (THOUSANDS[10000],))
    
    # Rules & Suffixes
    cursor.execute("INSERT INTO raw_lexemes (numeric_value, surface_form, category) VALUES (10, ?, 'TEEN_PREFIX')", (RULES["teen_prefix"],))
    cursor.execute("INSERT INTO raw_lexemes (numeric_value, surface_form, category) VALUES (0, ?, 'TEEN_SUFFIX')", (RULES["teen_suffix"],))

    # --- 3. Dynamic Structural Compounding Views ---
    # Replaces flat generation loops with an on-the-fly cross-product map
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS view_crystalized_teens AS
    SELECT 
        (p.numeric_value + o.numeric_value) AS computed_value,
        (p.surface_form || ' ' || o.surface_form || s.surface_form) AS surface_form,
        'TEEN_COMPOUND' AS category
    FROM raw_lexemes p
    CROSS JOIN raw_lexemes o
    CROSS JOIN raw_lexemes s
    WHERE p.category = 'TEEN_PREFIX' 
      AND o.category = 'ONE' 
      AND s.category = 'TEEN_SUFFIX';
    """)
    
    conn.commit()
    print(f"✨ Staged Myaamia dictionary elements cleanly inside: {db_path}")
    
    # Quick debug view execution to show how it calculates "mataathswi nkotiaasi" (11)
    cursor.execute("SELECT computed_value, surface_form FROM view_crystalized_teens LIMIT 2;")
    print("Preview of view compilation:", cursor.fetchall())
    conn.close()

if __name__ == "__main__":
    build_myaamia_search_index()
