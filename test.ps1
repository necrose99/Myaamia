$code = @'
import os
import re
import sys
import time
import random
import logging
import warnings
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

# 1. Initialize logging matrix to record network anomalies gracefully
logging.basicConfig(
    filename='pipeline.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    encoding='utf-8'
)

# Clear noisy beautifulsoup layout mismatches on Python 3.14
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

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

def fetch_upstream_pos_politely(url, ilda_id):
    """Polite, rate-limited extractor targeting upstream dictionary elements."""
    if not url:
        return None
    try:
        req = Request(url, headers={
            'User-Agent': 'MyaamiaOntolexPipeline/1.2 (Linguistic Research Framework; contact: black@GitHub/Myaamia)'
        })
        with urlopen(req, timeout=12) as response:
            page_soup = BeautifulSoup(response.read(), "html.parser")
            pos_element = page_soup.find("span", class_="part-of-speech") or page_soup.find(text=re.compile(r"Verb|Noun|Particle", re.I))
            if pos_element:
                text_label = pos_element.get_text().strip().lower()
                for label, uri in KNOWN_POS_LABELS.items():
                    if label in text_label:
                        logging.info(f"ID {ilda_id}: Successfully resolved POS '{uri}' from web target.")
                        return uri
            
            logging.warning(f"ID {ilda_id}: Connected successfully, but no matching POS label structure was resolved on page.")
                        
    except Exception as e:
        logging.error(f"ID {ilda_id}: Fetch exception triggered for URI <{url}>. Context: {e}")
        print(f"   ⚠️ Logged network anomaly for entry ID {ilda_id}.")
    return None

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

def parse_tmx_to_ontolex(tmx_content, crawl_missing=False):
    soup = BeautifulSoup(tmx_content, "html.parser")

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
        "# --- Language / lexicon dataset metadata ---",
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
        '    dcterms:description "Derived from ilda_full.tmx, parsed cleanly via HTML fallbacks"@en .',
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
    all_tus = soup.find_all("tu")
    total_entries = len(all_tus)
    
    print(f"📊 Discovered {total_entries} records within the source matrix file.")
    logging.info(f"System initialization completed. Parsing {total_entries} records.")

    for index, tu in enumerate(all_tus, 1):
        props = {p.get("type"): p.get_text(strip=True) for p in tu.find_all("prop")}
        ilda_id = props.get("x-ilda-id")
        ilda_url = props.get("x-ilda-url")
        letter = props.get("x-letter")
        form_type = props.get("x-form-type")  

        tuv_mia = tu.find(lambda tag: tag.name == "tuv" and tag.get("xml:lang", "").lower() == "mia") or tu.find("tuv", {"lang": "mia"})
        tuv_en = tu.find(lambda tag: tag.name == "tuv" and tag.get("xml:lang", "").lower() in ["en-us", "en"]) or tu.find("tuv", {"lang": "en-us"})
        
        mia_text = tuv_mia.find("seg").get_text(strip=True) if (tuv_mia and tuv_mia.find("seg")) else ""
        if not mia_text:
            continue

        en_text = tuv_en.find("seg").get_text(strip=True) if (tuv_en and tuv_en.find("seg")) else ""

        base_id = f"ilda_{ilda_id}" if ilda_id else safe_local_name(mia_text, f"entry_{index}")
        safe_id = base_id
        n = 1
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

        # Network lookup execution block
        if pos_is_heuristic and crawl_missing and ilda_url:
            print(f"   🔍 [{index}/{total_entries}] Deep scanning item fields via network frame...")
            web_pos = fetch_upstream_pos_politely(ilda_url, ilda_id)
            if web_pos:
                pos_uri = web_pos
                pos_is_heuristic = False
                print(f"      ✅ Found Part of Speech: {pos_uri}")
            else:
                print("      ❌ No precise Part of Speech resolved upstream.")
            
            delay = random.uniform(2.0, 4.5)
            time.sleep(delay)

        # --- LexicalEntry Output Assembly ---
        ttl_lines.append(f"ex:{safe_id} rdf:type ontolex:LexicalEntry ;")
        ttl_lines.append(f'    rdfs:label "{escape_ttl_literal(mia_text)}"@mia ;')
        
        if not has_gloss:
            ttl_lines.append("    alg:unresolvedGloss true ;")

        if pos_uri:
            ttl_lines.append(f"    lexinfo:partOfSpeech {pos_uri} ;")
            if pos_is_heuristic:
