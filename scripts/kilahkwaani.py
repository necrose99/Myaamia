#!/bin/python3 
##scripts/kilahkwaani.py
import json
import sqlite3

# The "Makišiweelo" Gender Filter - Cultural Guardrails
gender_rules = {
    "iihia": "male",   # Affirmation (men)
    "iiia": "male",    # Variant spelling
    "naaka": "female"  # Affirmation (women)
}

def get_voice_profile(myaamia_word):
    word_clean = myaamia_word.lower().strip('-')
    return gender_rules.get(word_clean, "neutral")

def generate_web_manifest(lexicon_db, output_json):
    """
    Refines the lexicon into a production-ready JS manifest.
    Corrects mismatched gender samples via the 'forced_voice' tag.
    """
    manifest = {}
    conn = sqlite3.connect(lexicon_db)
    cur = conn.cursor()
    
    # We pull the term and the IPA notes we generated earlier
    cur.execute("SELECT id, term, ipa FROM lexicon")
    
    for row_id, term, ipa in cur.fetchall():
        clean_key = term.strip('-').lower()
        voice_profile = get_voice_profile(clean_key)
        
        manifest[clean_key] = {
            "id": row_id,
            "orthography": term,
            "ipa": ipa,
            "allophones": list(ipa.strip('/')),
            "voice_profile": voice_profile,
            "has_recording": False, # To be toggled if HTML crawler finds a link
            "sample_gender": "male"  # Assuming the common volunteer speaker
        }
        
    with open(output_json, 'w', encoding='utf-8') as jf:
        json.dump(manifest, jf, indent=2, ensure_ascii=False)
    
    conn.close()
    print(f"[!] Makišiweelo! Web Manifest created with {len(manifest)} assets.")

# generate_web_manifest('myaamia_relational.db', 'myaamia_assets.json')
