import re
import sys
import uuid
from bs4 import BeautifulSoup
from xml.dom import minidom
import xml.etree.ElementTree as ET

# --- Upstream Authority Mappings for Algic / Algonquian Lineages ---
GLOTTOLOG_MAP = {
    "algic_stock": "https://glottolog.org/resource/languoid/id/algi1248.ttl",
    "algonquian_subgroup": "https://glottolog.org/resource/languoid/id/algo1257.ttl",
    "miami_illinois_language": "https://glottolog.org/resource/languoid/id/miam1252.ttl",
}

# Feature Detection Rules matching your OntoLex parser
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

def extract_gloss_annotations(en_text):
    clean = en_text
    speaker = None
    animacy = None
    
    for pattern, term in SPEAKER_PATTERNS:
        if pattern.search(clean):
            speaker = term
            clean = pattern.sub("", clean)
            break
            
    for pattern, term in ANIMACY_PATTERNS:
        if pattern.search(clean):
            animacy = term
            clean = pattern.sub("", clean)
            break
            
    clean = re.sub(r"\(\s*,?\s*\)", "", clean)
    clean = re.sub(r"\s{2,}", " ", clean)
    return clean.strip(" ,"), speaker, animacy

def build_enriched_flextext(tmx_content):
    # Parse the TMX payload via BeautifulSoup XML parser module
    soup = BeautifulSoup(tmx_content, "xml")
    
    # --- Create Native ElementTree Root Matching FlexInterlinear.xsd ---
    doc_node = ET.Element("document", version="2")
    interlinear_node = ET.SubElement(doc_node, "interlinear-text")
    
    # Inject Title Text Anchor
    t_node = ET.SubElement(interlinear_node, "item", type="title", lang="en")
    t_node.text = "Myaamia ILDA Corpus via bs4 Amalgamation Engine"
    
    # Inject Upstream Authority Mappings from GLOTTOLOG_MAP
    for key, url in GLOTTOLOG_MAP.items():
        meta_node = ET.SubElement(interlinear_node, "item", type=f"x-glottolog-{key.replace('_', '-')}", lang="en")
        meta_node.text = url

    paragraphs_node = ET.SubElement(interlinear_node, "paragraphs")
    paragraph_node = ET.SubElement(paragraphs_node, "paragraph")
    phrases_node = ET.SubElement(paragraph_node, "phrases")

    phrase_idx = 1

    # --- Loop over Translation Units (<tu>) using bs4 ---
    for tu in soup.find_all("tu"):
        # Map flat properties into a lookup dictionary
        props = {p.get("type"): p.get_text(strip=True) for p in tu.find_all("prop")}
        
        ilda_id = props.get("x-ilda-id")
        ilda_url = props.get("x-ilda-url")
        letter = props.get("x-letter")
        form_type = props.get("x-form-type", "word")
        entry_id = props.get("x-lift-entry-id")
        sense_id = props.get("x-lift-sense-id")

        # Resolve language variants
        tuv_mia = tu.find("tuv", {"xml:lang": "mia"}) or tu.find("tuv", {"lang": "mia"})
        tuv_en = (tu.find("tuv", {"xml:lang": "en-US"}) or tu.find("tuv", {"lang": "en-US"}) or
                  tu.find("tuv", {"xml:lang": "en"}) or tu.find("tuv", {"lang": "en"}))

        if tuv_mia and tuv_en:
            mia_seg = tuv_mia.find("seg")
            en_seg = tuv_en.find("seg")
            
            if mia_seg and en_seg:
                mia_text = mia_seg.get_text(strip=True)
                en_text = en_seg.get_text(strip=True)
                
                if not mia_text:
                    continue

                # Run feature keyword detection on english gloss
                clean_gloss, speaker, animacy = extract_gloss_annotations(en_text)

                # Initialize Phrase Block Node
                phrase_guid = str(uuid.uuid4())
                phrase_node = ET.SubElement(phrases_node, "phrase", guid=phrase_guid)
                
                # Structural Segment Count
                seg_item = ET.SubElement(phrase_node, "item", type="segnum", lang="en")
                seg_item.text = f"{phrase_idx}"

                # Append Extracted Structural metadata attributes to phrase tier
                if ilda_id:
                    ET.SubElement(phrase_node, "item", type="x-ilda-id", lang="en").text = ilda_id
                if ilda_url:
                    ET.SubElement(phrase_node, "item", type="x-ilda-url", lang="en").text = ilda_url
                if letter:
                    ET.SubElement(phrase_node, "item", type="x-alphabet-letter", lang="en").text = letter
                if entry_id:
                    ET.SubElement(phrase_node, "item", type="x-lift-entry-id", lang="en").text = entry_id
                if sense_id:
                    ET.SubElement(phrase_node, "item", type="x-lift-sense-id", lang="en").text = sense_id
                if animacy:
                    ET.SubElement(phrase_node, "item", type="x-morph-animacy", lang="en").text = animacy
                if speaker:
                    ET.SubElement(phrase_node, "item", type="x-speaker-restriction", lang="en").text = speaker

                # Surface transcriptions
                ET.SubElement(phrase_node, "item", type="txt", lang="mia").text = mia_text
                ET.SubElement(phrase_node, "item", type="gls", lang="en").text = clean_gloss

                # Word Tokenization layer
                words_node = ET.SubElement(phrase_node, "words")
                for token in mia_text.split():
                    clean_token = token.strip(".,!?;:()\"")
                    if not clean_token:
                        continue
                        
                    word_node = ET.SubElement(words_node, "word")
                    ET.SubElement(word_node, "item", type="txt", lang="mia").text = clean_token
                    
                    # Embed morphemic parameters using x-form-type properties
                    morphemes_node = ET.SubElement(word_node, "morphemes")
                    morph_node = ET.SubElement(morphemes_node, "morph", type=form_type)
                    ET.SubElement(morph_node, "item", type="txt", lang="mia").text = clean_token
                    
                phrase_idx += 1

    # Format output tree with clean indentations
    raw_xml = ET.tostring(doc_node, encoding="utf-8")
    dom = minidom.parseString(raw_xml)
    return dom.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python amalgamate_to_flex.py <input.tmx> <output.flextext>")
    else:
        with open(sys.argv[1], "r", encoding="utf-8") as infile:
            compiled_xml = build_enriched_flextext(infile.read())
            
        with open(sys.argv[2], "w", encoding="utf-8") as outfile:
            outfile.write(compiled_xml)
            
        print(f"[+] Amalgamation complete. Output saved to: {sys.argv[2]}")
