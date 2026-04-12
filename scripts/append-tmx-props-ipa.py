import xml.etree.ElementTree as ET
import os

# --- ISO MAPPING TABLES ---
# Add your tables here as you find them.
MAPS = {
    "mia": { # Miami-Illinois
        "š": "ʃ", "ii": "iː", "ee": "eː", "aa": "aː", "oo": "oː"
    },
    "sha": { # Shawnee
        "th": "θ", "sh": "ʃ", "aa": "ɑː", "ee": "eː", "ii": "iː", "oo": "oː"
    },
    "sac": { # Meskwaki (Fox)
        "ch": "tʃ", "sh": "ʃ", "aa": "ɑ", "ee": "æ", "ii": "i", "oo": "ɔ"
    },
    "kic": { # Kickapoo
        "th": "θ", "ch": "tʃ", "aa": "ɑ", "ee": "ɛ", "ii": "i", "oo": "ɔ"
    },
    # PLACEHOLDERS: Add bft, arp, chy, cre etc. here.
}

def generate_ipa(text, lang_code):
    if not text or lang_code not in MAPS:
        return ""
    
    mapping = MAPS[lang_code]
    ipa = text.lower()
    # Replace longer strings first to prevent partial replacement
    for orth in sorted(mapping.keys(), key=len, reverse=True):
        ipa = ipa.replace(orth, mapping[orth])
    return f"/{ipa}/"

def process_tmx(input_path, output_path):
    # Register namespaces to keep the XML clean
    ET.register_namespace('xml', 'http://www.w3.org/XML/1998/namespace')
    
    tree = ET.parse(input_path)
    root = tree.getroot()
    body = root.find("body")

    for tu in body.findall("tu"):
        # Identify the language of the first TUV
        first_tuv = tu.find("tuv")
        if first_tuv is None: continue
        
        lang = first_tuv.get("{http://www.w3.org/XML/1998/namespace}lang")
        source_seg = first_tuv.find("seg")
        
        if source_seg is not None and source_seg.text:
            ipa_val = generate_ipa(source_seg.text, lang)
            
            # Create the <prop> if it doesn't exist
            if ipa_val:
                # Standard TMX: props must come BEFORE tuv elements
                prop = ET.Element("prop", {"type": "x-ipa"})
                prop.text = ipa_val
                tu.insert(0, prop)

    # Pretty print and save
    ET.indent(tree, space="  ")
    tree.write(output_path, encoding="UTF-8", xml_declaration=True)

# Usage# Expanded Mapping for the Algic Family
MAPS = {
    # --- CENTRAL ---
    "kic_us": { # Oklahoma Kickapoo
        "aa": "ɑ", "ee": "ɛ", "ii": "i", "oo": "ɔ", "th": "θ", "ch": "tʃ"
    },
    "kic_mx": { # Mexican Kickapoo (accounting for Spanish loans/influence)
        "aa": "ɑ", "ee": "ɛ", "ii": "i", "oo": "ɔ", "th": "θ", "ch": "tʃ",
        "rr": "r", "ll": "j" # Spanish loanword phonemes
    },
    "pot": { # Potawatomi (vowel syncope is heavy here)
        "mb": "m", "nd": "n", "sh": "ʃ", "zh": "ʒ"
    },
    "cre": { # Cree (General)
        "ê": "eː", "î": "iː", "â": "aː", "ô": "oː", "th": "ð"
    },
    
    # --- PLAINS (Placeholders) ---
    "bft": {}, # Blackfoot: complex clusters, glottal stops '
    "chy": {}, # Cheyenne: pitch/tone markers are crucial for gSpeak
    
    # --- EASTERN ---
    "mic": { # Mi'kmaq
        "p": "b", "t": "d", "k": "g", "q": "ɣ" # Voicing depends on environment
    }
}
# Inside your append-tmx-props-ipa.py loop
if lang in ["kic_us", "kic_mx"]:
    # Regional property to help gSpeak select the right voice profile
    region_prop = ET.Element("prop", {"type": "x-region"})
    region_prop.text = "Oklahoma" if lang == "kic_us" else "Coahuila"
    tu.insert(0, region_prop)
  MAPS.update({
    "mua": { # Munsee Delaware
        "sh": "ʃ", "zh": "ʒ", "ch": "tʃ", "ii": "iː", "ee": "eː", "aa": "aː", "oo": "oː",
        "xw": "xʷ", "kw": "kʷ", "ə": "ə" # Often written as 'u' or 'e' in older texts
    },
    "unm": { # Unami (Lenape)
        "x": "x", "š": "ʃ", "č": "tʃ", "ë": "ə", "à": "a", # Unami uses unique diacritics
        "ii": "iː", "ee": "eː", "uu": "uː"
    }
})
def repair_lenape(text):
    repairs = {
        "Ã«": "ë", # The schwa artifact
        "Å¡": "š", # The sh sound
        "Ä": "č", # The ch sound
        "Ã ": "à"  # Grave accent for short vowels
    }
    for bad, good in repairs.items():
        text = text.replace(bad, good)
    return text
# Expanded mapping for Algic Master enrichment
ALGIC_GLOBAL_MAPS = {
    # --- EASTERN (Lenape / Delaware / Abenaki) ---
    "mua": {"sh":"ʃ", "zh":"ʒ", "ch":"tʃ", "xw":"xʷ", "kw":"kʷ", "ii":"iː", "ee":"eː", "aa":"aː", "oo":"oː", "ë":"ə"},
    "unm": {"š":"ʃ", "č":"tʃ", "ë":"ə", "ii":"iː", "ee":"eː", "uu":"uː", "x":"x"},
    "mic": {"ch":"tʃ", "kw":"kʷ", "p":"b", "t":"d", "k":"g", "q":"ɣ"}, # Voiced variants
    "abe": {"8":"oː", "ô":"ɑ̃", "ch":"tʃ", "sh":"ʃ"}, # '8' is a common artifact for /o/ or /w/

    # --- PLAINS (Highly divergent phonology) ---
    "bft": {"'":"ʔ", "ks":"ks", "hp":"ʰp", "ht":"ʰt", "hk":"ʰk", "ii":"iː", "aa":"aː", "oo":"oː"},
    "chy": {"á":"a˦", "é":"e˦", "ó":"o˦", "å":"ḁ", "ė":"e̥", "ô":"o̥", "š":"ʃ"}, # Tones + Whispered vowels
    "arp": {"'":"ʔ", "3":"θ", "ee":"ɛː", "oo":"ɔː", "ii":"iː", "uu":"uː"},

    # --- CENTRAL (The 'ja' and 'ii' logic) ---
    "cre": {"ê":"eː", "î":"iː", "â":"aː", "ô":"oː", "th":"ð", "y":"j"},
    "oji": {"aa":"aː", "ii":"iː", "oo":"oː", "e":"eː", "sh":"ʃ", "zh":"ʒ", "hc":"htʃ"},
    "men": {"ae":"æ", "oe":"ø", "q":"ʔ", "aeh":"æh", "ee":"eː"},
    "pot": {"sh":"ʃ", "zh":"ʒ", "ch":"tʃ", "ë":"ə"}
}
import xml.etree.ElementTree as ET

def enrich_tmx_with_ipa(input_tmx, output_tmx):
    # Keep the XML structure clean
    ET.register_namespace('xml', 'http://www.w3.org/XML/1998/namespace')
    tree = ET.parse(input_tmx)
    root = tree.getroot()
    
    for tu in root.findall(".//tu"):
        # Get language code from the first TUV
        first_tuv = tu.find("tuv")
        if first_tuv is None: continue
        lang = first_tuv.get("{http://www.w3.org/XML/1998/namespace}lang")
        
        # Pull text from the segment
        seg = first_tuv.find("seg")
        if seg is None or not seg.text: continue
        
        # Roman -> IPA processing
        raw_text = seg.text
        # Check if we have a map for this ISO code
        mapping = ALGIC_GLOBAL_MAPS.get(lang, {})
        
        ipa_processed = raw_text.lower()
        # Process longer strings first (e.g., 'sh' before 's')
        for roman, ipa in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
            ipa_processed = ipa_processed.replace(roman, ipa)
            
        # Create or update <prop type="x-ipa">
        # TMX standard: Props MUST come before TUVs
        existing_prop = tu.find("prop[@type='x-ipa']")
        if existing_prop is not None:
            existing_prop.text = f"/{ipa_processed}/"
        else:
            new_prop = ET.Element("prop", {"type": "x-ipa"})
            new_prop.text = f"/{ipa_processed}/"
            tu.insert(0, new_prop)

    tree.write(output_tmx, encoding="utf-8", xml_declaration=True)


# process_tmx("Algic_master.tmx", "Algic_master_enriched.tmx")
