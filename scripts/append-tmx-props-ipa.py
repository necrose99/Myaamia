import xml.etree.ElementTree as ET

XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

# --- MASTER MAP ---
ALGIC_MAPS = {
    # --- CENTRAL ---
    "mia": {  # Miami-Illinois
        "š": "ʃ", "ii": "iː", "ee": "eː", "aa": "aː", "oo": "oː"
    },
    "sha": {  # Shawnee
        "th": "θ", "sh": "ʃ", "aa": "ɑː", "ee": "eː", "ii": "iː", "oo": "oː"
    },
    "sac": {  # Meskwaki (Fox)
        "ch": "tʃ", "sh": "ʃ", "aa": "ɑ", "ee": "æ", "ii": "i", "oo": "ɔ"
    },

    # --- KICKAPOO VARIANTS ---
    "kic_us": {  # Oklahoma Kickapoo
        "aa": "ɑ", "ee": "ɛ", "ii": "i", "oo": "ɔ",
        "th": "θ", "ch": "tʃ"
    },
    "kic_mx": {  # Mexican Kickapoo (Spanish influence)
        "aa": "ɑ", "ee": "ɛ", "ii": "i", "oo": "ɔ",
        "th": "θ", "ch": "tʃ",
        "rr": "r", "ll": "j"
    },

    "pot": {  # Potawatomi
        "mb": "m", "nd": "n", "sh": "ʃ", "zh": "ʒ"
    },
    "cre": {  # Cree
        "ê": "eː", "î": "iː", "â": "aː", "ô": "oː",
        "th": "ð", "y": "j"
    },
    "oji": {  # Ojibwe
        "aa": "aː", "ii": "iː", "oo": "oː",
        "e": "eː", "sh": "ʃ", "zh": "ʒ", "hc": "htʃ"
    },
}
    # EASTERN
    "mua": {"sh":"ʃ","zh":"ʒ","ch":"tʃ","xw":"xʷ","kw":"kʷ","ii":"iː","ee":"eː","aa":"aː","oo":"oː","ë":"ə"},
    "unm": {"š":"ʃ","č":"tʃ","ë":"ə","ii":"iː","ee":"eː","uu":"uː","x":"x"},
    "mic": {"ch":"tʃ","kw":"kʷ","p":"b","t":"d","k":"g","q":"ɣ"},
    "abe": {"8":"oː","ô":"ɑ̃","ch":"tʃ","sh":"ʃ"},

    # PLAINS
    "bft": {"'":"ʔ","ii":"iː","aa":"aː","oo":"oː"},
    "chy": {"á":"a˦","é":"e˦","ó":"o˦","š":"ʃ"},
    "arp": {"'":"ʔ","3":"θ","ee":"ɛː","oo":"ɔː","ii":"iː","uu":"uː"},
}

# --- TEXT REPAIR ---
def repair_text(text: str) -> str:
    repairs = {
        "Ã«": "ë",
        "Å¡": "š",
        "Ä": "č",
        "Ã ": "à"
    }
    for bad, good in repairs.items():
        text = text.replace(bad, good)
    return text


# --- NORMALIZE LANGUAGE TAG ---
def normalize_lang(lang: str) -> str:
    if not lang:
        return ""
    return lang.lower().replace("-", "_")


# --- IPA GENERATION ---
def generate_ipa(text: str, lang: str) -> str:
    lang = normalize_lang(lang)

    mapping = ALGIC_MAPS.get(lang)
    if not mapping:
        return ""

    text = repair_text(text.lower())

    for k, v in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
        text = text.replace(k, v)

    return f"/{text}/"


# --- SAFE PROP INSERT ---
def upsert_prop(tu, prop_type, value):
    existing = tu.find(f"prop[@type='{prop_type}']")
    if existing is not None:
        existing.text = value
    else:
        prop = ET.Element("prop", {"type": prop_type})
        prop.text = value
        tu.insert(0, prop)


# --- REGION HANDLER ---
def apply_region(tu, lang):
    if lang == "kic_us":
        upsert_prop(tu, "x-region", "Oklahoma")
    elif lang == "kic_mx":
        upsert_prop(tu, "x-region", "Coahuila")


# --- MAIN PROCESS ---
def enrich_tmx(input_path, output_path):
    ET.register_namespace('xml', 'http://www.w3.org/XML/1998/namespace')

    tree = ET.parse(input_path)
    root = tree.getroot()

    for tu in root.findall(".//tu"):
        tuv = tu.find("tuv")
        if tuv is None:
            continue

        lang = tuv.get(XML_LANG)
        seg = tuv.find("seg")

        if seg is None or not seg.text:
            continue

        ipa = generate_ipa(seg.text, lang)
        if ipa:
            upsert_prop(tu, "x-ipa", ipa)

        apply_region(tu, normalize_lang(lang))

    ET.indent(tree, space="  ")
    tree.write(output_path, encoding="utf-8", xml_declaration=True)


# Example usage
# enrich_tmx("Algic_master.tmx", "Algic_master_enriched.tmx")
