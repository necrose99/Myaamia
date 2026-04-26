# Unified Algic Language Codes (ISO 639-3 + Atlas/Gothenburg variants)
algic_array = [
    # Reconstructed / Proto
    "alg-x-proto", # Proto-Algonquian (PA)
    
    # Plains Branch
    "bla", "arp", "ats", "chy", "bft",
    
    # Central Branch (Great Lakes / Shield)
    "men", "cre", "csw", "crj", "atj", "nsk", "moos", "crm", 
    "pot", "oji", "otw", "ciw", "alq", "ojb", "ojg", "ojs", 
    "mia", "sac", "kic_us", kic_mx","sha",
    
    # Eastern Branch (Maritime / New England / Atlantic)
    "mic", "abe", "aaq", "mal", "moo", "mua", "unm", "wamp",
    "mas", "nrn", "qpi", "nnt", "pow", "pmk", "psk", "mjy",
    
    # Ritwan (California "Cousins")
    "wiy", "yur",
    
    # External Reference
    "en-US" "la" "fr" "es_mx" # latin for genis sp etc... 
]
import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime

def make_algic_tmx_skeleton(filename, entries=10):
    # Setup TMX Structure
    tmx = ET.Element("tmx", version="1.4")
    header = ET.SubElement(tmx, "header", {
        "creationtool": "Ollama-Dispatcher",
        "creationtoolversion": "2.0",
        "segtype": "phrase",
        "adminlang": "en-US",
        "srclang": "en-US",
        "datatype": "PlainText",
        "creationdate": datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
    })
    body = ET.SubElement(tmx, "body")

    # Generate Skeleton Units
    for i in range(entries):
        tu = ET.SubElement(body, "tu", tuid=f"alg_unit_{i:04d}")
        
        # English Source Segment
        tuv_en = ET.SubElement(tu, "tuv", {"xml:lang": "en-US"})
        ET.SubElement(tuv_en, "seg").text = f"[Placeholder {i}]"
        
        # Populate all 45+ Algic Variants
        for code in algic_array:
            if code != "en-US":
                tuv = ET.SubElement(tu, "tuv", {"xml:lang": code})
                ET.SubElement(tuv, "seg").text = "" # Empty for Ollama/Weblate

    # Write to File
    xml_str = minidom.parseString(ET.tostring(tmx)).toprettyxml(indent="  ")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(xml_str)

if __name__ == "__main__":
    make_algic_tmx_skeleton("Algic.tmx", entries=100)
    print("✅ Algic.tmx with 45+ variants created. Ready for GitHub/Weblate.")
