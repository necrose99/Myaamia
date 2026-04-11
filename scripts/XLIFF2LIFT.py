import os
import sys
import glob
from lxml import etree as ET
from datetime import datetime

# Your Order of Battle
# Your "Order of Battle" for Algic Languages
ALGIC_ARRAY = [
    "alg-x-proto", "bla", "arp", "ats", "chy", "bft",
    "men", "cre", "csw", "crj", "atj", "nsk", "moos", "crm", 
    "pot", "oji", "otw", "ciw", "alq", "ojb", "ojg", "ojs", 
    "mia", "sac", "kic", "sha", "mic", "abe", "aaq", "mal", 
    "moo", "mua", "unm", "wamp", "mas", "nrn", "qpi", "nnt", 
    "pow", "pmk", "psk", "mjy", "wiy", "yur", "en-US", "Latin", "es_mx", "fr"
]
def xliff_to_lift(xlf_path):
    lift_path = xlf_path.replace('.xlf', '.lift').replace('.xliff', '.lift')
    
    # LIFT Header reconstruction
    root = ET.Element("lift", version="0.13", producer="XLIFF2LIFT.py")
    header = ET.SubElement(root, "header")
    fields = ET.SubElement(header, "fields")
    ET.SubElement(fields, "field", tag="import-date").text = datetime.now().isoformat()

    tree = ET.parse(xlf_path)
    # XLIFF Namespaces can be tricky
    ns = {'x': 'urn:oasis:names:tc:xliff:document:1.2'}

    for unit in tree.xpath("//x:trans-unit", namespaces=ns):
        entry_id = unit.get('id')
        source_text = unit.find("x:source", namespaces=ns).text
        target_text = unit.find("x:target", namespaces=ns).text
        
        # Determine roles based on algic_array
        # Assume source is usually English and target is Algic for this example
        entry = ET.SubElement(root, "entry", id=entry_id)
        
        # Lexical Unit (The Headword)
        lex_unit = ET.SubElement(entry, "lexical-unit")
        form = ET.SubElement(lex_unit, "form", lang="mia") # Priority to Myaamia
        ET.SubElement(form, "text").text = target_text
        
        # Sense and Gloss
        sense = ET.SubElement(entry, "sense", id=f"sense_{entry_id}")
        gram_info = ET.SubElement(sense, "grammatical-info", value="Noun") # Default
        gloss = ET.SubElement(sense, "gloss", lang="en")
        ET.SubElement(gloss, "text").text = source_text

    # Write out the SIL XML
    with open(lift_path, "wb") as f:
        f.write(ET.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=True))
    
    print(f"✅ Transmogrified {xlf_path} to {lift_path}")

if __name__ == "__main__":
    files = sys.argv[1:] if len(sys.argv) > 1 else ["*.xlf"]
    for pattern in files:
        for f in glob.glob(pattern):
            xliff_to_lift(f)
