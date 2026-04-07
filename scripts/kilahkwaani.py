# /bin/python3/env
#kilahkwaani.py
import json

def generate_web_manifest(tmx_data, lexicon_db, output_json):
    """
    Creates a manifest for JS assets.
    If no audio URL exists in the HTML, the IPA serves as the TTS driver.
    """
    manifest = {}
    
    # Connect to your deduplicated DB
    conn = sqlite3.connect(lexicon_db)
    cur = conn.cursor()
    
    # Fetch all headwords with their IPA
    cur.execute("SELECT term, ipa FROM lexicon")
    for term, ipa in cur.fetchall():
        # clean the term for the key
        clean_key = term.strip('-').lower()
        
        manifest[clean_key] = {
            "orthography": term,
            "ipa": ipa,
            "allophones": list(ipa.strip('/')),
            "has_recording": False, # Default to false
            "tts_fallback": f"speechSynthesis.speak(new SpeechSynthesisUtterance('{ipa}'))"
        }
        
    with open(output_json, 'w', encoding='utf-8') as jf:
        json.dump(manifest, jf, indent=2, ensure_ascii=False)
    
    print(f"[!] Web Manifest created: {output_json}")
# The "Makišiweelo" Gender Filter
gender_rules = {
    "iihia": "male",
    "iiia": "male",
    "naaka": "female"
}

def get_voice_profile(myaamia_word):
    word_clean = myaamia_word.lower().strip('-')
    return gender_rules.get(word_clean, "neutral") 
