import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime

# The list of Algic ISO/Gothenburg codes
algic_codes = [
    "bft", "arp", "ats", "chy", "men", "cre", "csw", "crj", "atj", 
    "pot", "oji", "otw", "ciw", "mia", "sac", "kic", "sha", "mic", 
    "abe", "aaq", "mal", "moo", "mua", "unm", "alg-x-proto"
]

def create_empty_algic_tmx(output_file, num_entries=10):
    tmx = ET.Element("tmx", version="1.4")
    header = ET.SubElement(tmx, "header", {
        "creationtool": "Ollama-Dispatcher-Bot",
        "creationtoolversion": "1.0",
        "segtype": "phrase",
        "adminlang": "en",
        "srclang": "en",
        "datatype": "PlainText",
        "creationdate": datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
    })
    body = ET.SubElement(tmx, "body")

    for i in range(num_entries):
        tu = ET.SubElement(body, "tu", tuid=f"algic_unit_{i:04d}")
        
        # Source Language (English)
        tuv_en = ET.SubElement(tu, "tuv", {"xml:lang": "en"})
        ET.SubElement(tuv_en, "seg").text = f"[Source Text {i}]"
        
        # All Algic Targets (Empty for Weblate/Ollama to fill)
        for code in algic_codes:
            tuv = ET.SubElement(tu, "tuv", {"xml:lang": code})
            ET.SubElement(tuv, "seg").text = ""

    # Pretty print for GitHub/Git readability
    xml_str = minidom.parseString(ET.tostring(tmx)).toprettyxml(indent="  ")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(xml_str)

if __name__ == "__main__":
    create_empty_algic_tmx("Algic_Skeleton.tmx", num_entries=50)
    print("✅ Created Algic.tmx with 25 codes (expandable to 45). Ready for Weblate.")
