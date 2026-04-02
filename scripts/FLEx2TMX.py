import lxml.etree as ET
from datetime import datetime

def flex_lift_to_tmx(lift_file, tmx_output):
    # LIFT files use standard XML but often have specific trait/field structures
    tree = ET.parse(lift_file)
    root = tree.getroot()
    
    # TMX Root Setup
    tmx_root = ET.Element("tmx", version="1.4")
    header = ET.SubElement(tmx_root, "header", {
        "segtype": "phrase", "adminlang": "en-US", "srclang": "mia",
        "datatype": "PlainText", "creationdate": datetime.now().strftime("%Y%m%dT%H%M%SZ")
    })
    body = ET.SubElement(tmx_root, "body")

    for entry in root.xpath("//entry"):
        # 1. Extract Myaamia Lexeme (\lx)
        # FLEx LIFT stores this in lexical-unit/form
        mia_text = entry.xpath("./lexical-unit/form[@lang='mia']/text/text()")
        if not mia_text: continue
        
        tu = ET.SubElement(body, "tu")
        
        # 2. Extract Latin (\nt) back to TMX Property
        # FLEx often stores scientific names as 'trait' or 'field'
        latin = entry.xpath("./field[@type='scientific-name']/form/text/text()") or \
                entry.xpath("./note/form/text/text()[contains(., 'Latin:')]")
        
        if latin:
            # Clean "Latin: " prefix if it was stored in a note
            clean_latin = latin[0].replace("Latin: ", "").strip()
            prop = ET.SubElement(tu, "prop", type="scientific_name")
            prop.text = clean_latin

        # 3. Extract English Gloss (\ge)
        eng_text = entry.xpath("./sense/gloss[@lang='en']/text/text()")
        
        # Build TMX Translation Units
        # Myaamia (Core)
        tuv_mia = ET.SubElement(tu, "tuv")
        tuv_mia.set("{http://www.w3.org/XML/1998/namespace}lang", "mia")
        ET.SubElement(tuv_mia, "seg").text = mia_text[0].strip()

        # English (Bridge)
        if eng_text:
            tuv_en = ET.SubElement(tu, "tuv")
            tuv_en.set("{http://www.w3.org/XML/1998/namespace}lang", "en-US")
            ET.SubElement(tuv_en, "seg").text = eng_text[0].strip()

    # Save to your dedicated rack's storage
    tmx_tree = ET.ElementTree(tmx_root)
    tmx_tree.write(tmx_output, encoding="utf-8", xml_declaration=True, pretty_print=True)
    print(f"✅ Exported {lift_file} to {tmx_output} (TMX 1.4)")

if __name__ == "__main__":
    # Point this at your FLEx LIFT export
    flex_lift_to_tmx('Myaamia_Export.lift', 'Myaamia_Master.tmx')
