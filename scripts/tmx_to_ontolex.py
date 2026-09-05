import re
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# ilda_full.tmx structure (confirmed against the real file):
#   header: x-iso639-3=mia, x-glottocode=miam1252, x-entry-count=2589,
#           x-stem-convention: "$word- = bound stem; $word = free/uninflected form"
#   <tu tuid="ilda-N">
#     <prop type="x-ilda-id">N</prop>
#     <prop type="x-ilda-url">https://mc.miamioh.edu/ilda-myaamia/dictionary/entries/N</prop>
#     <prop type="x-letter">a</prop>
#     <prop type="x-form-type">stem|word</prop>
#     <tuv xml:lang="mia"><seg>...</seg></tuv>
#     <tuv xml:lang="en-US"><seg>...</seg></tuv>
#   </tu>
#
# This is a BROWSE-INDEX snapshot only (per the x-note in the header) —
# it has no POS field and no separate animacy/register field. Those either
# (a) live inside the English gloss as free text ("(women only)", "used
#     only by men", "(out of reach, inanimate)"), extractable by regex, or
# (b) only exist on the per-entry page (e.g. .../entries/2083 shows
#     "(No-object Verb)" plus full inflection tables) and are NOT in this
#     TMX at all — that requires a separate per-ID fetch pass.
# ---------------------------------------------------------------------------

# --- gloss-embedded annotation patterns -------------------------------------
# Order matters: check speaker-restriction before generic animacy, and strip
# each matched span out of the clean gloss as it's found.

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

# Known Myaamia Center POS labels as they appear on per-entry pages, e.g.
# "(No-object Verb)". Not present in this TMX's glosses, but kept here so
# the same extractor can be reused once per-entry data is merged in.
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
    """Pull speaker-restriction / animacy markers out of a free-text gloss.
    Returns (clean_gloss, speaker_restriction_or_None, animacy_or_None,
    matched_raw_spans). Everything returned as *_is_heuristic=True since
    it's pattern-matched from prose, not a structured source field."""
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
            break  # one restriction per entry is enough for this corpus

    for pattern, term in ANIMACY_PATTERNS:
        m = pattern.search(clean)
        if m:
            animacy = term
            matched.append(m.group(0))
            clean = pattern.sub("", clean)
            break

    # tidy up leftover punctuation/whitespace from stripped parentheticals
    clean = re.sub(r"\(\s*,?\s*\)", "", clean)
    clean = re.sub(r"\s{2,}", " ", clean)
    clean = re.sub(r"\s+,", ",", clean)
    clean = re.sub(r",\s*,", ",", clean)
    clean = clean.strip(" ,")

    return clean, speaker, animacy, matched


def detect_pos_fallback(en_text, form_type):
    """Weak POS fallback for entries with no per-entry-page POS available.
    Flagged as heuristic — replace with real per-entry POS when merged in.
    Returns (pos_uri_or_None, is_heuristic). None means genuinely unresolved
    — do NOT default bound stems to 'particle': particles are free invariant
    words, and most bound ($word-) stems in Algonquian are verbal, so a
    'Particle' default would be a false, misleading claim at scale."""
    lowered = en_text.lower()
    tokens = lowered.split()

    for label, uri in KNOWN_POS_LABELS.items():
        if label in lowered:
            return uri, False  # came straight from a known label, not guessed

    if re.search(r"^\d+$", en_text) or any(
        w in tokens for w in ["one", "two", "three", "four", "five"]
    ):
        return "lexinfo:Numeral", True

    if any(t in tokens for t in ["him", "her", "them"]):
        return "lexinfo:TransitiveVerb", True

    if lowered.endswith("ing") or lowered.startswith("to "):
        return "lexinfo:Verb", True

    if any(a in tokens for a in ["a", "an", "the"]):
        return "lexinfo:Noun", True

    if form_type == "word" and len(tokens) <= 2:
        # Short, unbound, uninflected free forms are the only class where
        # 'particle' is a defensible guess (interjections, discourse
        # particles). Still flagged as heuristic.
        return "lexinfo:LexicalParticle", True

    return None, True


def parse_tmx_to_ontolex(tmx_content):
    soup = BeautifulSoup(tmx_content, "xml")

    ttl_lines = [
        "@prefix ontolex: <http://www.w3.org/ns/lemon/ontolex#> .",
        "@prefix lime:     <http://www.w3.org/ns/lemon/lime#> .",
        "@prefix lexinfo:  <http://www.lexinfo.net/ontology/3.0/lexinfo#> .",
        "@prefix morph:    <http://www.w3.org/ns/lemon/morph#> .",
        "@prefix alg:      <http://example.org/algic-vocab#> .",
        "@prefix rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix xsd:      <http://www.w3.org/2001/XMLSchema#> .",
        "@prefix skos:     <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix dcterms:  <http://purl.org/dc/terms/> .",
        "# NOTE: mc.miamioh.edu does not serve RDF/linked data, so entry URIs",
        "# stay under ex: (this repo's own namespace). mia: identifies the",
        "# LANGUAGE/dataset itself, not individual entries, to avoid implying",
        "# false dereferenceability at the Center's domain.",
        "@prefix mia:      <https://mc.miamioh.edu/ilda-myaamia/> .",
        "@prefix ex:       <http://example.org/mia-lexicon#> .",
        "",
        "# --- Language / lexicon dataset metadata (OntoLex-Lemon lime module) ---",
        "mia:language a lime:Language ;",
        '    lime:iso639P3PCode "mia" ;',
        '    rdfs:label "Miami-Illinois (Myaamia / Irenwa)"@en ;',
        "    alg:glottocode <https://glottolog.org/resource/languoid/id/miam1252> ;",
        "    alg:languageFamily alg:CentralAlgonquian .",
        "",
        "mia:lexicon a lime:Lexicon ;",
        '    dcterms:title "Miami-Illinois ILDA Browse-Index Lexicon"@en ;',
        "    lime:language mia:language ;",
        "    dcterms:source <https://mc.miamioh.edu/ilda-myaamia/dictionary/entries> ;",
        '    dcterms:description "Derived from ilda_full.tmx, a browse-index snapshot (headwords + glosses only)"@en .',
        "",
        "# --- Language family classification (SKOS broader chain) ---",
        "# 'Central Algonquian' is a traditional AREAL grouping, not a confirmed",
        "# genetic subgroup within Algonquian — flagged here rather than",
        "# asserted as settled genetic classification.",
        "alg:Algic a skos:Concept ;",
        '    skos:prefLabel "Algic"@en .',
        "alg:Algonquian a skos:Concept ;",
        '    skos:prefLabel "Algonquian"@en ;',
        "    skos:broader alg:Algic .",
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
        form_type = props.get("x-form-type")  # 'stem' or 'word'

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
    with open(sys.argv[1], encoding="utf-8") as f:
        content = f.read()
    print(parse_tmx_to_ontolex(content))
