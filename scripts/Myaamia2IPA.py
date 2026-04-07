import re

def myaamia_to_ipa(text):
    # Mapping table for Myaamia phonemes
    mapping = {
        'š': 'ʃ',    # Esh
        'č': 'tʃ',   # Check (often written as 'hc' or 'c')
        'aa': 'aː',  # Long vowel
        'ee': 'ɛː',
        'ii': 'iː',
        'oo': 'oː',
        'hk': 'ʰk',  # Pre-aspiration
        'ht': 'ʰt',
        'hp': 'ʰp',
        'ay': 'aj',  # Diphthongs
        'aw': 'aw'
    }
    
    # Standardize input (handle the Å¡ encoding artifacts)
    text = text.replace('Å¡', 'š').lower()
    
    # Apply mappings
    ipa = text
    for orth, phon in mapping.items():
        ipa = ipa.replace(orth, phon)
    
    return f"/{ipa}/"

# Example: Mahweewa (Wolf)
# print(myaamia_to_ipa("mahweewa")) -> /mahwɛːwa/
