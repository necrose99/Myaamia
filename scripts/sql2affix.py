import sqlite3
import os

def generate_affix_file(db_path, iso_code):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    aff_filename = f"{iso_code.upper()}_US-{iso_code.capitalize()}.aff"
    
    # 1. Standard Header (UTF-8 is mandatory for Algic orthography)
    header = [
        "SET UTF-8",
        "WORDCHARS '",
        "CHECKCOMPOUND 2",
        "COMPOUNDMIN 2",
        f"# Affix rules for {iso_code} generated from SQL Shards",
        "\n"
    ]

    # 2. Extract Rules Grouped by Flag
    query = """
    SELECT type, flag, stripping, append, condition 
    FROM affix_rules 
    WHERE iso = ? 
    ORDER BY type, flag
    """
    rules = cur.execute(query, (iso_code,)).fetchall()

    # 3. Process and Count Rules (Hunspell requires a count per flag group)
    grouped_rules = {}
    for r_type, flag, strip, app, cond in rules:
        key = (r_type, flag)
        if key not in grouped_rules:
            grouped_rules[key] = []
        grouped_rules[key].append(f"{r_type} {flag} {strip} {app} {cond}")

    # 4. Write to File
    with open(aff_filename, 'w', encoding='utf-8') as f:
        f.writelines("\n".join(header))
        
        for (r_type, flag), rule_lines in grouped_rules.items():
            # Hunspell Format: TYPE FLAG CROSSPRODUCT COUNT
            f.write(f"{r_type} {flag} Y {len(rule_lines)}\n")
            for line in rule_lines:
                f.write(f"{line}\n")
            f.write("\n")

    print(f"✅ Created {aff_filename} with {len(rules)} rules.")
    conn.close()

if __name__ == "__main__":
    # Example usage for Myaamia
    generate_affix_file('rag-sqlite.sql', 'mia')
  algic_isos = ['mia', 'pot', 'oji', 'cre', 'sha']

for iso in algic_isos:
    # 1. Run your existing tmx2dict logic
    tmx_to_hunspell_dict('Algic.tmx', f"{iso}.dic", target_lang=iso)
    # 2. Run the new SQL-to-Affix logic
    generate_affix_file('rag-sqlite.sql', iso)

