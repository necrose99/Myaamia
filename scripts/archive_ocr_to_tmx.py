import re
import xml.etree.ElementTree as ET
from datetime import datetime

def parse_le_boulanger_ocr(ocr_text_file, output_tmx):
    root = ET.Element("tmx", version="1.4")
    body = ET.SubElement(root, "body")
    
    with open(ocr_text_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # The manuscript is alphabetical (abbaisser to vuider)
    # This regex looks for French keywords followed by Miami strings
    # Note: 18th-century '8' is used for 'ou/w' sounds
    entries = re.findall(r'([A-Z][a-z\-]+)\s+([a-z8\-\s]+)', content)

    for i, (fr, mia) in enumerate(entries):
        tu = ET.SubElement(body, "tu", tuid=f"leboulanger_{i}")
        
        # French (Source)
        tuv_fr = ET.SubElement(tu, "tuv")
        tuv_fr.set("{http://www.w3.org/XML/1998/namespace}lang", "fr")
        ET.SubElement(tuv_fr, "seg").text = fr.strip()
        
        # Miami-Illinois (Target)
        tuv_mia = ET.SubElement(tu, "tuv")
        tuv_mia.set("{http://www.w3.org/XML/1998/namespace}lang", "mia")
        ET.SubElement(tuv_mia, "seg").text = mia.strip()
        
        # Placeholder for English (to be filled by your Translation Bot)
        tuv_en = ET.SubElement(tu, "tuv")
        tuv_en.set("{http://www.w3.org/XML/1998/namespace}lang", "en-US")
        ET.SubElement(tuv_en, "seg").text = "[PENDING TRANSLATION]"

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_tmx, encoding="utf-8", xml_declaration=True)
    print(f"✅ Extracted {len(entries)} Jesuit-era shards to {output_tmx}")

if __name__ == "__main__":
    # Download the 'Full Text' from Archive.org first
    parse_le_boulanger_ocr('le_boulanger_fulltext.txt', 'jesuit_mia_shards.tmx')
