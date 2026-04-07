import re
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

def clean_content(text):
    """Removes HTML, MHTML bloat, and extra whitespace."""
    if not text: return ""
    # Strip MHTML/Blink frame IDs
    text = re.sub(r'\+saved\.frame-[a-z0-9]+@mhtml\S+', '', text)
    # Strip DOM paths
    text = re.sub(r'\.div\.\S+', '', text)
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def create_tmx(json_data, output_file):
    # TMX Root setup
    tmx = ET.Element('tmx', version="1.4")
    header = ET.SubElement(tmx, 'header', creationtool="PythonCleanup", 
                          datatype="PlainText", segtype="sentence", 
                          adminlang="en-us", srclang="en")
    body = ET.SubElement(tmx, 'body')

    for unit in json_data.get('units', []):
        src_text = clean_content(unit.get('source', ''))
        tgt_text = clean_content(unit.get('target', ''))

        # Only export if there is actual content and it's not just a DOM path
        if src_text and not src_text.startswith('.'):
            tu = ET.SubElement(body, 'tu')
            
            # Source Segment (English)
            tuv_en = ET.SubElement(tu, 'tuv', {'xml:lang': 'en'})
            ET.SubElement(tuv_en, 'seg').text = src_text
            
            # Target Segment (Myaamia / mia)
            tuv_mia = ET.SubElement(tu, 'tuv', {'xml:lang': 'mia'})
            ET.SubElement(tuv_mia, 'seg').text = tgt_text

    # Prettify and Save
    xml_str = minidom.parseString(ET.tostring(tmx)).toprettyxml(indent="  ")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(xml_str)

# Execution
# with open('ilda-dictionary.json', 'r') as f:
#    data = json.load(f)
#    create_tmx(data, 'ilda_clean.tmx')
