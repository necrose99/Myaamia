import os
import re
import sys
import time
import random
import logging
import warnings
import xml.etree.ElementTree as ET

warnings.filterwarnings("ignore")

logging.basicConfig(
    filename='pipeline.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    encoding='utf-8'
)

GLOTTOLOG_MAP = {
    "algic_stock": "https://glottolog.org",
    "algonquian_subgroup": "https://glottolog.org",
    "miami_illinois_language": "https://glottolog.org",
}

SPEAKER_PATTERNS = [
    (re.compile(r"\(women only\)", re.I), "alg:FemaleSpeaker"),
    (re.compile(r"used only by women", re.I), "alg:FemaleSpeaker"),
    (re.compile(r"\(men only\)", re.I), "alg:MaleSpeaker"),
    (re.compile(r"used only by men", re.I), "alg:MaleSpeaker"),
]

ANIMACY_PATTERNS = [
    (re.compile(r"\binanimate\b", re.I), "alg:Inanimate"),
    (re.compile(r"\banimate\b", re.I), "alg:Animate"),
]

KNOWN_POS_LABELS = {
    "no-object verb": "alg:NoObjectVerb",
    "object verb": "alg:ObjectVerb",
    "common noun": "lexinfo:CommonNoun",
    "interjection": "lexinfo:Interjection",
    "transitive verb": "lexinfo:TransitiveVerb",
    "intransitive verb": "lexinfo:IntransitiveVerb",
}

def escape_ttl_literal(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')

def safe_local_name(text, fallback):
    ident = re.sub(r"[^a-zA-Z0-9_]", "", text.replace(" ", "_").replace("-", "_"))
    return ident if ident else fallback

def extract_gloss_annotations(en_text):
    clean = en_text
    speaker = None
    animacy = None
    matched = []

    for pattern, term in SPEAKER_PATTERNS:
        m = pattern.search(clean)
        if m:
            speaker = term
            matched.append(m.group(0))
            clean = pattern.sub("", clean)
            break  

    for pattern, term in ANIMACY_PATTERNS:
        m = pattern.search(clean)
        if m:
            animacy = term
            matched.append(m.group(0))
            clean = pattern.sub("", clean)
            break

    clean = re.sub(r"\(\s*,?\s*\)", "", clean)
    clean = re.sub(r"\s{2,}", " ", clean)
    clean = re.sub(r"\s+,", ",", clean)
    clean = re.sub(r",\s*,", ",", clean)
    return clean.strip(" ,"), speaker, animacy, matched

def detect_pos_fallback(en_text, form_type):
    lowered = en_text.lower()
    tokens = lowered.split()
    for label, uri in KNOWN_POS_LABELS.items():
        if label in lowered:
            return uri, False  
    if re.search(r"^\d+$", en_text) or any(w in tokens for w in ["one", "two", "three", "four", "five"]):
        return "lexinfo:Numeral", True
    if any(t in tokens for t in ["him", "her", "them"]):
        return "lexinfo:TransitiveVerb", True
    if lowered.endswith("ing") or lowered.startswith("to "):
        return "lexinfo:Verb", True
    if any(a in tokens for a in ["a", "an", "the"]):
        return "lexinfo:Noun", True
    if form_type == "word" and len(tokens) <= 2:
        return "lexinfo:LexicalParticle", True
    return None, True

def process_pipeline(input_tmx, output_ttl, start_idx=0, end_idx=None):
    print("📖 Initializing XML layout parsing structures...")
    
    tree = ET.parse(input_tmx)
    root = tree.getroot()
    all_tus = root.findall(".//tu")
    total_found = len(all_tus)

    sliced_tus = all_tus[start_idx:end_idx] if end_idx is not None else all_tus[start_idx:]
    total_to_process = len(sliced_tus)
    
    print(f"📊 Total Records: {total_found} | Range constraint: [{start_idx}:{end_idx if end_idx else total_found}] ({total_to_process} items).")

    # Use clean f-strings to prevent raw domain fallback variables
    ttl_lines = [
        "@prefix ontolex: <http://w3.org> .",
        "@prefix lime:     <http://w3.org> .",
        "@prefix lexinfo:  <http://lexinfo.net> .",
        "@prefix morph:    <http://w3.org> .",
        "@prefix alg:      <http://example.org> .",
        "@prefix rdfs:     <http://w3.org> .",
        "@prefix rdf:      <http://w3.org> .",
        "@prefix xsd:      <http://w3.org> .",
        "@prefix skos:     <http://w3.org> .",
        "@prefix dcterms:  <http://purl.org> .",
        "@prefix mia:      <https://miamioh.edu> .",
        "@prefix ex:       <http://example.org> .",
        "",
        "mia:language a lime:Language ;",
        '    lime:iso639P3PCode "mia" ;',
        '    rdfs:label "Miami-Illinois (Myaamia / Irenwa)"@en ;',
        f"    alg:glottocode <{GLOTTOLOG_MAP['miami_illinois_language']}> ;",
        "    alg:languageFamily alg:CentralAlgonquian .",
        "",
        "mia:lexicon a lime:Lexicon ;",
        '    dcterms:title "Miami-Illinois ILDA Browse-Index Lexicon"@en ;',
        "    lime:language mia:language ;",
        "    dcterms:source <https://miamioh.edudictionary/entries> ;",
        '    dcterms:description "Derived from ilda_full.tmx via direct XML Stream handling"@en .',
        "",
        "alg:Algic a skos:Concept ;",
        f"    rdfs:seeAlso <{GLOTTOLOG_MAP['algic_stock']}> ;",
        '    skos:prefLabel "Algic"@en .',
        "",
        "alg:Algonquian a skos:Concept ;",
        f"    rdfs:seeAlso <{GLOTTOLOG_MAP['algonquian_subgroup']}> ;",
        '    skos:prefLabel "Algonquian"@en ;',
        "    skos:broader alg:Algic .",
        "",
        "alg:CentralAlgonquian a skos:Concept ;",
        '    skos:prefLabel "Central Algonquian"@en ;',
        "    skos:broader alg:Algonquian ;",
        '    rdfs:comment "Areal/geographic grouping, not an established genetic subgroup"@en .',
        "",
    ]

    seen_ids = set()
    entry_ids = []

    for loop_idx, tu in enumerate(sliced_tus, 1):
        global_idx = start_idx + loop_idx - 1
        
        props = {p.get("type"): p.text.strip() for p in tu.findall("prop") if p.text}
        ilda_id = props.get("x-ilda-id")
        ilda_url = props.get("x-ilda-url")
        letter = props.get("x-letter")
        form_type = props.get("x-form-type")

        tuvs = tu.findall("tuv")
        mia_text = ""
        en_text = ""
        
        for tuv in tuvs:
            lang_val = ""
            for k, v in tuv.attrib.items():
                if "lang" in k.lower():
                    lang_val = v.lower()
            if "mia" in lang_val:
                seg_node = tuv.find("seg")
                if seg_node is not None and seg_node.text:
                    mia_text = seg_node.text.strip()
            if "en" in lang_val:
                seg_node = tuv.find("seg")
                if seg_node is not None and seg_node.text:
                    en_text = seg_node.text.strip()

        if not mia_text:
            continue

        safe_id = f"ilda_{ilda_id}" if ilda_id else f"entry_{global_idx}"
        n = 1
        base_id = safe_id
        while safe_id in seen_ids:
            n += 1
            safe_id = f"{base_id}_{n}"
        seen_ids.add(safe_id)
        entry_ids.append(safe_id)

        has_gloss = bool(en_text.strip())
        if has_gloss:
            clean_gloss, speaker, animacy, matched = extract_gloss_annotations(en_text)
            pos_uri, pos_is_heuristic = detect_pos_fallback(clean_gloss, form_type)
        else:
            clean_gloss = "[No English translation present in index source record]"
            speaker, animacy = None, None
            pos_uri, pos_is_heuristic = None, True

        ttl_lines.append(f"ex:{safe_id} rdf:type ontolex:LexicalEntry ;")
        ttl_lines.append(f'    rdfs:label "{escape_ttl_literal(mia_text)}"@mia ;')
        if not has_gloss:
            ttl_lines.append("    alg:unresolvedGloss true ;")
        if pos_uri:
            ttl_lines.append(f"    lexinfo:partOfSpeech {pos_uri} ;")
        if animacy:
            ttl_lines.append(f"    alg:animacy {animacy} ;")
        if letter:
            ttl_lines.append(f'    alg:ildaLetter "{letter}" ;')
        ttl_lines.append(f"    ontolex:canonicalForm ex:{safe_id}_form .")

        ttl_lines.append(f"ex:{safe_id}_form rdf:type ontolex:Form ;")
        if form_type == "stem":
            ttl_lines.append("    rdf:type morph:Stem ;")
        ttl_lines.append(f'    ontolex:writtenRep "{escape_ttl_literal(mia_text)}"@mia .')

        ttl_lines.append(f"ex:{safe_id}_sense rdf:type ontolex:LexicalSense ;")
        ttl_lines.append(f"    ontolex:isSenseOf ex:{safe_id} ;")
        ttl_lines.append(f'    rdfs:comment "{escape_ttl_literal(clean_gloss)}"@en ;')
        if speaker:
            ttl_lines.append(f"    alg:speakerRestriction {speaker} ;")
        if ilda_id:
            ttl_lines.append(f'    alg:ildaId "{ilda_id}"^^xsd:integer ;')
        if ilda_url:
            ttl_lines.append(f"    rdfs:seeAlso <{ilda_url}> ;")
        ttl_lines.append("    rdfs:isDefinedBy <http://myaamiadictionary.org> .")
        ttl_lines.append("")

    if entry_ids:
        ttl_lines.append("# --- Lexicon -> entry links ---")
        for eid in entry_ids:
            ttl_lines.append(f"mia:lexicon lime:entry ex:{eid} .")
        ttl_lines.append("")

    print(f"💾 Exporting generated triples safely to {output_ttl}...")
    with open(output_ttl, "w", encoding="utf-8") as f:
        f.write("\n".join(ttl_lines))
    print("🚀 Transformation processing sequence complete!")

if __name__ == "__main__":
    INPUT_FILE  = "ilda_full.tmx"
    OUTPUT_FILE = "mia_ilda_lexicon_full.ttl"
    START_VALUE = 0
    END_VALUE   = None  # Processes all entries instantly
    
    process_pipeline(INPUT_FILE, OUTPUT_FILE, start_idx=START_VALUE, end_idx=END_VALUE)
