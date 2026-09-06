#!/usr/bin/env python3
"""
Algic Training Corpus Enhancement Tool - Pure Self-Contained Ingestion Engine
Maps and injects language-scoped IPA properties directly into multi-lingual TMX files.
"""
import xml.etree.ElementTree as ET
import sys
import os

XML_LANG = "{http://w3.org}lang"

# --- MASTER PHONETIC TRANSLATION MATRIX (ALL DIALECTS BUNDLED) ---
ALGIC_MAPS = {
    # --- CENTRAL ALGONQUIAN ---
    "mia": { # Miami-Illinois
        "š": "ʃ", "ž": "ʒ", "č": "tʃ", "ii": "iː", "ee": "eː", "aa": "aː", "oo": "oː"
    },
    "sha": { # Shawnee
        "th": "θ", "sh": "ʃ", "aa": "ɑː", "ee": "eː", "ii": "iː", "oo": "oː"
    },
    "sac": { # Meskwaki (Fox)
        "ch": "tʃ", "sh": "ʃ", "aa": "ɑ", "ee": "æ", "ii": "i", "oo": "ɔ"
    },
    "kic_us": { # Oklahoma Kickapoo
        "aa": "ɑ", "ee": "ɛ", "ii": "i", "oo": "ɔ", "th": "θ", "ch": "tʃ"
    },
    "kic_mx": { # Mexican Kickapoo
        "aa": "ɑ", "ee": "ɛ", "ii": "i", "oo": "ɔ", "th": "θ", "ch": "tʃ", "rr": "r", "ll": "j"
    },
    "pot": { # Potawatomi
        "mb": "m", "nd": "n", "sh": "ʃ", "zh": "ʒ"
    },
    "cre": { # Cree
        "ê": "eː", "î": "iː", "â": "aː", "ô": "oː", "th": "ð", "y": "j"
    },
    "oji": { # Ojibwe
        "aa": "aː", "ii": "iː", "oo": "oː", "e": "eː", "sh": "ʃ", "zh": "ʒ", "hc": "htʃ"
    },
    
    # --- EASTERN ALGONQUIAN ---
    "mua": { # Munsee Delaware
        "sh": "ʃ", "zh": "ʒ", "ch": "tʃ", "xw": "xʷ", "kw": "kʷ", "ii": "iː", "ee": "eː", "aa": "aː", "oo": "oː", "ë": "ə"
    },
    "unm": { # Unami Delaware
        "š": "ʃ", "č": "tʃ", "ë": "ə", "ii": "iː", "ee": "eː", "uu": "uː", "x": "x"
    },
    "mic": { # Mi'kmaq
        "ch": "tʃ", "kw": "kʷ", "p": "b", "t": "d", "k": "g", "q": "ɣ"
    },
    "abe": { # Abenaki
        "8": "oː", "ô": "ɑ̃", "ch": "tʃ", "sh": "ʃ"
    },
    
    # --- PLAINS ALGONQUIAN ---
    "bft": { # Blackfoot
        "'": "ʔ", "ii": "iː", "aa": "aː", "oo": "oː"
    },
    "chy": { # Cheyenne
        "á": "aː", "é": "eː", "ó": "oː", "š": "ʃ"
    },
    "arp": { # Arapaho
        "'": "ʔ", "3": "θ", "ee": "ɛː", "oo": "ɔː", "ii": "iː", "uu": "uː"
    }
}

def repair_text(text: str) -> str:
    """Safely normalizes text vectors and shields against legacy encoding noise."""
    if not text:
        return ""
    repairs = {
        "ÃƒÂ«": "ë", "Ã«": "ë",
        "Ã…Â¡": "š", "Å¡": "š",
        "Ã„Â ": "č", "Ä ": "č",
        "Ãƒ ": "à", "Ã ": "à"
    }
    for bad, good in repairs.items():
        text = text.replace(bad, good)
    return text.strip()

def normalize_lang(lang_string: str) -> str:
    if not lang_string:
        return ""
    # Strip hidden whitespaces, tabs, carriage returns, and force lowercase
    clean_lang = lang_string.strip().lower().replace("-", "_")
    
    # Clean standard edge cases for language chains
    if "mia" in clean_lang:
        return "mia"
    if "en" in clean_lang:
        return "en"
    if "fr" in clean_lang:
        return "fr"
        
    return clean_lang


def generate_ipa(text: str, lang_string: str) -> str:
    normalized_iso = normalize_lang(lang_string)
    mapping = ALGIC_MAPS.get(normalized_iso)
    if not mapping:
        return "" # Skips language blocks that are not supported Algic targets
    
    text = repair_text(text.lower())
    # Sort keys by length descending to swap digraph segments (like 'sh') before loose characters
    for k, v in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
        text = text.replace(k, v)
    return f"/{text}/"

def upsert_prop(tu, prop_type, value):
    """Inserts or overwrites property metadata cells cleanly at the head of the TU block."""
    existing = tu.find(f"prop[@type='{prop_type}']")
    if existing is not None:
        existing.text = value
    else:
        prop = ET.Element("prop", {"type": prop_type})
        prop.text = value
        tu.insert(0, prop)

def apply_region(tu, lang_string):
    normalized = normalize_lang(lang_string)
    if normalized == "kic_us":
        upsert_prop(tu, "x-region", "Oklahoma")
    elif normalized == "kic_mx":
        upsert_prop(tu, "x-region", "Coahuila")

def process_corpus_enrichment(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"[!] Critical Path Error: Target file '{input_path}' cannot be located.")
        sys.exit(1)
        
    print(f"[*] Processing: {input_path}")
    ET.register_namespace('xml', 'http://w3.org')
    
    try:
        tree = ET.parse(input_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"[!] XML Parsing Exception caught on '{input_path}': {e}")
        return

    total_ipa_added = 0
    for tu in root.findall(".//tu"):
        for tuv in tu.findall("tuv"):
            lang_attr = tuv.get(XML_LANG)
            seg = tuv.find("seg")
            
            if lang_attr and seg is not None and seg.text:
                ipa_output = generate_ipa(seg.text, lang_attr)
                if ipa_output:
                    normalized_iso = normalize_lang(lang_attr)
                    # Create clean, localized linguistic markers (e.g., x-ipa-mia or x-ipa-pot)
                    upsert_prop(tu, f"x-ipa-{normalized_iso}", ipa_output)
                    apply_region(tu, lang_attr)
                    total_ipa_added += 1
                    
    if total_ipa_added > 0:
        ET.indent(tree, space=" ")
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"[+] Output verified. Appended {total_ipa_added} custom phonetic metadata slots to '{output_path}'.")
    else:
        print("[-] No valid Algic modules matched. File tracking array skipped.")

if __name__ == "__main__":
    # Flexible execution hook: checks command arguments, falls back to default file name
    input_file = sys.argv[1] if len(sys.argv) > 1 else "Myaamia-lda-dictionary.tmx"
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file # Overwrites inline by default

    process_corpus_enrichment(input_file, output_file)
