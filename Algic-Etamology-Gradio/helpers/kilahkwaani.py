# helpers/kilahkwaani.py
import json
from helpers.db_factory import DatabaseFactory

# Cultural Guardrails
GENDER_RULES = {
    "iihia": "male",
    "iiia": "male",
    "naaka": "female"
}

# Phonetic sequence mappings
G2P_MAPPING = [
    ('Å¡', 'š'), ('aa', 'aː'), ('ee', 'ɛː'), ('ii', 'iː'), ('oo', 'oː'),
    ('ay', 'aj'), ('aw', 'aw'), ('hk', 'ʰk'), ('ht', 'ʰt'), ('hp', 'ʰp'),
    ('hc', 'ʰtʃ'), ('š', 'ʃ'), ('č', 'tʃ'), ('c', 'tʃ')
]

IPA_TO_JS_TTS = {
    "aː": "aa", "ɛː": "eh", "iː": "ee", "oː": "oh",
    "aj": "eye", "aw": "ow", "ʰk": "hk", "ʰt": "ht",
    "ʰp": "hp", "ʰtʃ": "h-ch", "ʃ": "sh", "tʃ": "ch"
}

def myaamia_to_ipa(text: str) -> str:
    """Converts orthography to IPA."""
    if not text:
        return ""
    ipa = text.lower().strip('-')
    for orth, phon in G2P_MAPPING:
        ipa = ipa.replace(orth, phon)
    return f"/{ipa}/"

def get_voice_profile(word: str) -> str:
    """Returns voice profile gender based on cultural rules."""
    clean = word.lower().strip('-')
    return GENDER_RULES.get(clean, "neutral")

def ipa_to_tts_hint(ipa_str: str) -> str:
    """Provides Web Speech API phonetic hints for browser speech synthesis."""
    clean = ipa_str.strip('/')
    for ipa, approx in IPA_TO_JS_TTS.items():
        clean = clean.replace(ipa, approx)
    return clean

def build_speech_manifest(db_factory: DatabaseFactory) -> dict:
    """Constructs the runtime JS-ready speech dictionary."""
    rows = db_factory.get_lexical_entries()
    manifest = {}
    
    for row in rows:
        word = row['word']
        clean_key = word.strip('-').lower()
        ipa_val = row['ipa'] or myaamia_to_ipa(word)
        voice = row['voice_gender'] or get_voice_profile(clean_key)
        
        manifest[clean_key] = {
            "id": row['id'],
            "ilda_id": row['ilda_id'],
            "orthography": word,
            "lang": row['language_code'] or "mia",
            "ipa": ipa_val,
            "tts_hint": ipa_to_tts_hint(ipa_val),
            "voice": voice,
            "audio_url": row['audio_url'] or "",
            "has_recording": bool(row['audio_url']),
            "type": "gendered" if voice != "neutral" else "standard"
        }
    return manifest