
### git clone https://github.com/LibreTranslate/LTEngine --recursive
###cd LTEngine
####cargo build [--features cuda,vulkan,metal] --release
### for windows linux etc  pip install libretranslatepy etc ... 
# windows cargo build --features "cuda vulkan metal" --release


import xml.etree.ElementTree as ET
import requests

TMX_FILE = r"C:\Users\black\GitHub\Myaamia\ilda_full.tmx"
OUTPUT_FILE = r"C:\Users\black\GitHub\Myaamia\ilda_full_es.tmx"
TRANSLATE_URL = "http://127.0.0.1:5050/translate"

# XML namespace mapping for proper serialization
XML_NS = "{http://www.w3.org/XML/1998/namespace}"

def translate_to_Spanish(text):
    if not text or not text.strip():
        return ""
    try:
        payload = {
            "q": text,
            "source": "en",
            "target": "es",
            "format": "text",
            "api_key": ""
        }
        response = requests.post(TRANSLATE_URL, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json().get("translatedText", "")
    except Exception as e:
        print(f"Translation request error for '{text}': {e}")
    return ""

def process_tmx():
    # Register namespaces to preserve valid XML tags on output
    ET.register_namespace('xml', "http://www.w3.org/XML/1998/namespace")
    
    tree = ET.parse(TMX_FILE)
    root = tree.getroot()
    
    updated_count = 0

    # Iterate over all Translation Units (<tu>)
    for tu in root.iter("tu"):
        # Check if Spanish translation already exists in this TU
        has_es = any(
            tuv.attrib.get(f"{XML_NS}lang") == "es" or tuv.attrib.get("lang") == "es"
            for tuv in tu.findall("tuv")
        )
        if has_es:
            continue

        # Locate the English source segment
        en_text = None
        for tuv in tu.findall("tuv"):
            lang = tuv.attrib.get(f"{XML_NS}lang") or tuv.attrib.get("lang", "")
            if lang in ["en", "en-US", "en-GB"]:
                seg = tuv.find("seg")
                if seg is not None and seg.text:
                    en_text = seg.text
                    break

        # If English segment exists, query LTEngine and add Spanish tuv element
        if en_text:
            es_text = translate_to_Spanish(en_text)
            if es_text:
                es_tuv = ET.Element("tuv")
                es_tuv.set(f"{XML_NS}lang", "es")
                
                es_seg = ET.Element("seg")
                es_seg.text = es_text
                
                es_tuv.append(es_seg)
                tu.append(es_tuv)
                
                updated_count += 1
                print(f"[{updated_count}] EN: {en_text} -> es: {es_text}")

    # Write updated tree to output file
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"\nDone! Added Spanish translations to {updated_count} entries.")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    process_tmx()