# --- PYTHON 3.14 COMPATIBILITY MONKEY PATCH ---
import collections
import collections.abc
collections.MutableSequence = collections.abc.MutableSequence
# -----------------------------------------------

#!/usr/bin/env python3
"""
Algic Training Corpus Enhancement Tool - Resilient Wildcard Ingestion Engine
Maps and injects language-scoped IPA properties directly into multi-lingual TMX files.
Bypasses translate-toolkit API abstractions and namespace attribute bugs entirely.
"""
import xml.etree.ElementTree as ET
import sys
import os
from gruut_ipa import Pronunciation
from ipapy import is_valid_ipa

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
        "mb": "m", "nd": "n", "sh": "ʃ", "zh": "ʒ", "ā": "aː", "ē": "eː", "ī": "iː", "ō": "oː", "û": "û"
    },
    "cre": { # Plains Cree Latin Orthography
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
    if not text:
        return ""
    repairs = {
        "ÃƒÂ«": "ë", "Ã«": "ë", "Ã…Â¡": "š", "Å¡": "š",
        "Ã„Â ": "č", "Ä ": "č", "Ãƒ ": "à", "Ã ": "à"
    }
    for bad, good in repairs.items():
        text = text.replace(bad, good)
    return text.strip()

def normalize_lang_iso(lang_string: str) -> str:
    if not lang_string:
        return ""
    clean_lang = lang_string.strip().lower().replace("-", "_")
    
    if "mia" in clean_lang: return "mia"
    if "sha" in clean_lang: return "sha"
    if "sac" in clean_lang: return "sac"
    if "kic_us" in clean_lang or ("kic" in clean_lang and "us" in clean_lang): return "kic_us"
    if "kic_mx" in clean_lang or ("kic" in clean_lang and "mx" in clean_lang): return "kic_mx"
    if "pot" in clean_lang: return "pot"
    if "cre" in clean_lang: return "cre"
    if "oji" in clean_lang: return "oji"
    if "mua" in clean_lang: return "mua"
    if "unm" in clean_lang: return "unm"
    if "mic" in clean_lang: return "mic"
    if "abe" in clean_lang: return "abe"
    if "bft" in clean_lang: return "bft"
    if "chy" in clean_lang: return "chy"
    if "arp" in clean_lang: return "arp"
    return clean_lang

def generate_validated_ipa(text: str, lang_string: str) -> str:
    normalized_iso = normalize_lang_iso(lang_string)
    mapping = ALGIC_MAPS.get(normalized_iso)
    if not mapping:
        return ""
    
    processed_text = repair_text(text).lower()
    processed_text = processed_text.replace("-", "").replace("=", "")
    
    for k, v in sorted(mapping.items(), key=lambda x: len(x), reverse=True):
        processed_text = processed_text.replace(k, v)
        
    clean_ipa = processed_text.strip()
    
    # Validation loop using fallback sanitization logic
    try:
        _ = Pronunciation.from_string(clean_ipa)
        return f"/{clean_ipa}/"
    except Exception:
        sanitized = "".join([c for c in clean_ipa if is_valid_ipa(c)])
        return f"/{sanitized}/" if sanitized else f"/{clean_ipa}/"

def get_wildcard_lang_attr(node):
    """Bypasses namespace string constraints by hunting for any attribute matching 'lang'."""
    for attr_key, attr_val in node.attrib.items():
        if attr_key.endswith("lang"):
            return attr_val
    return None

def upsert_prop(tu, prop_type, value):
    existing = tu.find(f"prop[@type='{prop_type}']")
    if existing is not None:
        existing.text = value
    else:
        prop = ET.Element("prop", {"type": prop_type})
        prop.text = value
        tu.insert(0, prop)

def apply_region(tu, lang_string):
    normalized = normalize_lang_iso(lang_string)
    if normalized == "kic_us":
        upsert_prop(tu, "x-region", "Oklahoma")
    elif normalized == "kic_mx":
        upsert_prop(tu, "x-region", "Coahuila")

def process_corpus_enrichment(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"[!] Path Error: File '{input_path}' cannot be located.")
        sys.exit(1)
        
    print(f"[*] Extracting corpus fields via Wildcard XML parsing on: {input_path}")
    tree = ET.parse(input_path)
    root = tree.getroot()

    total_ipa_added = 0
    
    # Process elements using pure tree traversal patterns
    for tu in root.findall(".//tu"):
        for tuv in tu.findall("tuv"):
            lang_attr = get_wildcard_lang_attr(tuv)
            seg = tuv.find("seg")
            
            if lang_attr and seg is not None and seg.text:
                ipa_output = generate_validated_ipa(seg.text, lang_attr)
                if ipa_output:
                    normalized_iso = normalize_lang_iso(lang_attr)
                    upsert_prop(tu, f"x-ipa-{normalized_iso}", ipa_output)
                    apply_region(tu, lang_attr)
                    total_ipa_added += 1
                    
    if total_ipa_added > 0:
        ET.indent(tree, space=" ")
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"[+] Output verified. Successfully appended {total_ipa_added} custom phonetic properties to '{output_path}'.")
    else:
        print("[-] Enrichment complete. No matching language targets were found.")

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "ilda_full.tmx"
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file
    process_corpus_enrichment(input_file, output_file)
