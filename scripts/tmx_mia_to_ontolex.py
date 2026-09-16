import re
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# ilda_full.tmx structure (confirmed against the real file):
#   header: x-iso639-3=mia, x-glottocode=miam1252, x-entry-count=2589,
#           x-stem-convention: "$word- = bound stem; $word = free/uninflected form"
#   <tu tuid="ilda-N">
#     <prop type="x-ilda-id">N</prop>
#     <prop type="x-ilda-url">https://miamioh.edu</prop>
#     <prop type="x-letter">a</prop>
#     <prop type="x-form-type">stem|word</prop>
#     <tuv xml:lang="mia"><seg>...</seg></tuv>
#     <tuv xml:lang="en-US"><seg>...</seg></tuv>
#   </tu>
# ---------------------------------------------------------------------------

# --- Upstream Authority Mappings for Algic / Algonquian Lineages ---
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
    return clean.strip(" ,")


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


def parse_tmx_to_ontolex(tmx_content):
    soup = BeautifulSoup(tmx_content, "xml")

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
        "# --- Language / lexicon dataset metadata (OntoLex-Lemon lime module) ---",
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
        '    dcterms:description "Derived from ilda_full.tmx, a browse-index snapshot (headwords + glosses only)"@en .',
        "",
        "# --- Language family classification (SKOS broader chain with Upstream URIs) ---",
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

    for tu in soup.find_all("tu"):
        props = {p.get("type"): p.get_text(strip=True) for p in tu.find_all("prop")}
        ilda_id = props.get("x-ilda-id")
        ilda_url = props.get("x-ilda-url")
        letter = props.get("x-letter")
        form_type = props.get("x-form-type")  

        tuv_mia = tu.find("tuv", {"xml:lang": "mia"})
        tuv_en = tu.find("tuv", {"xml:lang": "en-US"})
        if not tuv_mia or not tuv_en:
            continue

        mia_text = tuv_mia.find("seg").get_text(strip=True) if tuv_mia.find("seg") else ""
        en_text = tuv_en.find("seg").get_text(strip=True) if tuv_en.find("seg") else ""
        if not mia_text:
            continue

        base_id = f"ilda_{ilda_id}" if ilda_id else safe_local_name(mia_text, None)
        safe_id = base_id
        n = 1
        while safe_id in seen_ids:
            n += 1
            safe_id = f"{base_id}_{n}"
        seen_ids.add(safe_id)
        entry_ids.append(safe_id)

        clean_gloss, speaker, animacy, matched = extract_gloss_annotations(en_text)
        pos_uri, pos_is_heuristic = detect_pos_fallback(clean_gloss, form_type)

        # --- LexicalEntry ---
        ttl_lines.append(f"ex:{safe_id} rdf:type ontolex:LexicalEntry ;")
        ttl_lines.append(f'    rdfs:label "{escape_ttl_literal(mia_text)}"@mia ;')
        if pos_uri:
            ttl_lines.append(f"    lexinfo:partOfSpeech {pos_uri} ;")
            if pos_is_heuristic:
                ttl_lines.append('    alg:heuristicSource "gloss-keyword-guess:no-per-entry-pos" ;')
        else:
            ttl_lines.append('    alg:posUnresolved true ;')
        if animacy:
            ttl_lines.append(f"    alg:animacy {animacy} ;")
            ttl_lines.append('    alg:heuristicSource "gloss-text-pattern:animacy" ;')
        if letter:
            ttl_lines.append(f'    alg:ildaLetter "{letter}" ;')
        ttl_lines.append(f"    ontolex:canonicalForm ex:{safe_id}_form .")

        # --- Form ---
        ttl_lines.append(f"ex:{safe_id}_form rdf:type ontolex:Form ;")
        if form_type == "stem":
            ttl_lines.append("    rdf:type morph:Stem ;")
        ttl_lines.append(f'    ontolex:writtenRep "{escape_ttl_literal(mia_text)}"@mia .')

        # --- Sense ---
        ttl_lines.append(f"ex:{safe_id}_sense rdf:type ontolex:LexicalSense ;")
        ttl_lines.append(f"    ontolex:isSenseOf ex:{safe_id} ;")
        ttl_lines.append(f'    rdfs:comment "{escape_ttl_literal(clean_gloss)}"@en ;')
        if speaker:
            ttl_lines.append(f"    alg:speakerRestriction {speaker} ;")
            ttl_lines.append('    alg:heuristicSource "gloss-text-pattern:speaker-restriction" ;')
        if ilda_id:
            ttl_lines.append(f'    alg:ildaId "{ilda_id}"^^xsd:integer ;')
        if ilda_url:
            ttl_lines.append(f"    rdfs:seeAlso <{ilda_url}> ;")
        ttl_lines.append("    rdfs:isDefinedBy <http://myaamiadictionary.org> .")
        ttl_lines.append("")

    if entry_ids:
        ttl_lines.append("# --- Lexicon -> entry links (lime:entry) ---")
        for eid in entry_ids:
            ttl_lines.append(f"mia:lexicon lime:entry ex:{eid} .")
        ttl_lines.append("")

    return "\n".join(ttl_lines)


if __name__ == "__main__":
    import sys
    # Enforce standard UTF-8 encoding across Windows/Linux file streams
    with open(sys.argv[1], encoding="utf-8") as f:
        content = f.read()
    print(parse_tmx_to_ontolex(content))
