import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime

def generate_algic_tmx(wordlist_path, codes_path, output_tmx):
    # 1. Load Language Codes
    langs = {}
    with open(codes_path, 'r') as f:
        for line in f:
            if ':' in line:
                code, name = line.strip().split(':')
                langs[code] = name

    # 2. Create TMX Root
    tmx = ET.Element("tmx", version="1.4")
    header = ET.SubElement(tmx, "header", {
        "creationtool": "Ollama-Algic-Bot",
        "creationtoolversion": "1.0",
        "segtype": "phrase",
        "o-tmf": "Myaamia-RAG",
        "adminlang": "en",
        "srclang": "en",
        "datatype": "PlainText",
        "creationdate": datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
    })
    body = ET.SubElement(tmx, "body")

    # 3. Process Wordlist (Assuming: English \t Myaamia)
    with open(wordlist_path, 'r') as f:
        for i, line in enumerate(f):
            parts = line.strip().split('\t')
            if len(parts) < 2: continue
            
            eng_val, mia_val = parts[0], parts[1]
            
            # Create Translation Unit (TU)
            tu = ET.SubElement(body, "tu", tuid=f"idx_{i:04d}")
            
            # English Variant
            tuv_en = ET.SubElement(tu, "tuv", {"xml:lang": "en"})
            ET.SubElement(tuv_en, "seg").text = eng_val
            
            # Myaamia Variant (Target Weight 1)
            tuv_mia = ET.SubElement(tu, "tuv", {"xml:lang": "mia"})
            ET.SubElement(tuv_mia, "seg").text = mia_val

            # 4. Generate Skeleton for remaining Algic Cousins
            for code in langs:
                if code not in ['en', 'mia']:
                    tuv_cousin = ET.SubElement(tu, "tuv", {"xml:lang": code})
                    # Leaves an empty segment for Ollama to fill during idle time
                    ET.SubElement(tuv_cousin, "seg").text = ""

    # 5. Pretty Print and Save
    xml_str = minidom.parseString(ET.tostring(tmx)).toprettyxml(indent="  ")
    with open(output_tmx, "w", encoding="utf-8") as f:
        f.write(xml_str)

if __name__ == "__main__":
    generate_algic_tmx('Word-List-Dictionary-ILDA.txt', 'algic_codes.txt', 'Algic.tmx')
    print("🚀 Algic.tmx generated with 45+ language variants.")
