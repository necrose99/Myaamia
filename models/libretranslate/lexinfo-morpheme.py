#!/usr/bin/env python3
import os
import json
import re
from rdflib import Graph, Namespace, URIRef

def find_myaamia_root():
    """
    Ascends dynamically from the script location to find the master repository root directory.
    Fallback safely defaults to the standard absolute hardcoded layout path if nested.
    """
    current = os.path.dirname(os.path.abspath(__file__))
    while current and os.path.basename(current) != "Myaamia":
        parent = os.path.dirname(current)
        if parent == current: # Reached drive root
            break
        current = parent
    
    if os.path.basename(current) == "Myaamia":
        return current
    return r"C:\Users\black\GitHub\Myaamia"

def extract_lexinfo_morphemes(ttl_path):
    print(f"[-] Deep-scanning root master semantic graph: {os.path.abspath(ttl_path)}")
    g = Graph()
    g.parse(ttl_path, format="turtle")
    
    morpheme_tokens = set()

    # Broad lookup: Grab every literal object value anywhere in the graph 
    # to swallow custom ontolex, lexinfo, or schema properties natively.
    for s, p, o in g:
        from rdflib import Literal
        if isinstance(o, Literal):
            literal_text = str(o).strip()
            if not literal_text or literal_text.startswith("http"):
                continue

            # 1. Capture explicit structural affixes: prefix- or -suffix
            if literal_text.startswith('-') or literal_text.endswith('-'):
                clean_affix = literal_text.replace('-', '').lower()
                if clean_affix and not re.search(r'\s', clean_affix): # ignore long descriptions
                    morpheme_tokens.add(clean_affix)

            # 2. Capture nested sub-tokens inside hyphenated word-chains
            if '-' in literal_text:
                # Split along dashes, dashes types, or whitespace variations
                fragments = [frag.lower() for frag in re.split(r'[-–—\s]+', literal_text) if frag]
                for frag in fragments:
                    # Filter for alphabet characters + specialized Myaamia orthography (š, ž)
                    if re.match(r'^[a-zA-Zšž]+$', frag):
                        morpheme_tokens.add(frag)

    # 3. Inject our verified system number suffix patterns from the counting rules (-aasi)
    teen_suffixes = ["nkotaasi", "niišaasi", "nihswaasi", "niiwaasi", "yaalanwaasi", 
                     "kaakaathswaasi", "swaahteethswaasi", "palaanaasi", "nkotimeneehkwaasi"]
    morpheme_tokens.update(teen_suffixes)

    return sorted(list(morpheme_tokens))

def update_argos_and_ministral_assets():
    # Target root masters dynamically using the correct filename
    root_dir = find_myaamia_root()
    ttl_path = os.path.join(root_dir, "mia_ilda_lexicon.ttl")
    
    # Absolute destinations for build environments
    argos_dir = os.path.join(root_dir, "models", "libretranslate")
    argos_vocab_path = os.path.join(argos_dir, "model", "vocabulary.json")
    
    ministral_dir = os.path.join(root_dir, "models", "Ministral-3B-Instruct")
    morphemes_output = os.path.join(ministral_dir, "morphemes_list.json")

    extracted_morphemes = extract_lexinfo_morphemes(ttl_path)
    if not extracted_morphemes:
        print("[!] No morphological elements were captured. Execution halted.")
        return

    print(f"[+] Successfully harvested {len(extracted_morphemes)} discrete structural tokens!")

    # Upgrade Argos / LibreTranslate Tracking Matrix
    os.makedirs(os.path.dirname(argos_vocab_path), exist_ok=True)
    if os.path.exists(argos_vocab_path):
        with open(argos_vocab_path, "r", encoding="utf-8") as f:
            argos_vocab = json.load(f)
        updated_argos = sorted(list(set(argos_vocab + extracted_morphemes)))
    else:
        updated_argos = extracted_morphemes

    with open(argos_vocab_path, "w", encoding="utf-8") as f:
        json.dump(updated_argos, f, indent=4, ensure_ascii=False)
    print(f"[+] Argos matrix updated: {argos_vocab_path}")

    # Upgrade Ministral-3B Registry Workspace
    os.makedirs(ministral_dir, exist_ok=True)
    with open(morphemes_output, "w", encoding="utf-8") as f:
        json.dump(extracted_morphemes, f, indent=2, ensure_ascii=False)
    print(f"[+] Ministral subword registry updated: {morphemes_output}")

if __name__ == "__main__":
    update_argos_and_ministral_assets()
