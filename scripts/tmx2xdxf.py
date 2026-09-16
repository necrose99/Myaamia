import sys
import xml.etree.ElementTree as ET

def tmx_to_xdxf_dynamic(tmx_path, output_path, title="Dictionary"):
    tree = ET.parse(tmx_path)
    root = tree.getroot()

    # Detect the two main languages from the first <tu>
    detected_langs = []
    first_tu = root.find(".//tu")
    if first_tu is not None:
        for tuv in first_tu.findall("tuv"):
            lang = tuv.attrib.get("{http://www.w3.org/XML/1998/namespace}lang") or tuv.attrib.get("lang")
            if lang and lang not in detected_langs:
                detected_langs.append(lang)
    
    if len(detected_langs) < 2:
        raise ValueError("Could not dynamically detect two languages in the TMX file.")

    lang_from, lang_to = detected_langs[0], detected_langs[1]

    # Initialize XDXF structure
    xdxf = ET.Element("xdxf", {
        "lang_from": lang_from.split("-")[0].upper(),
        "lang_to": lang_to.split("-")[0].upper(),
        "format": "logical"
    })
    
    full_name = ET.SubElement(xdxf, "full_name")
    full_name.text = title

    # Parse translation units
    for tu in root.findall(".//tu"):
        translations = {}

        for tuv in tu.findall("tuv"):
            lang = tuv.attrib.get("{http://www.w3.org/XML/1998/namespace}lang") or tuv.attrib.get("lang")
            seg = tuv.find("seg")
            
            if lang and seg is not None and seg.text:
                translations[lang] = seg.text.strip()

        if lang_from in translations and lang_to in translations:
            ar = ET.SubElement(xdxf, "ar")
            
            k = ET.SubElement(ar, "k")
            k.text = translations[lang_from]
            
            def_elem = ET.SubElement(ar, "def")
            def_elem.text = translations[lang_to]

    # Output file write
    output_tree = ET.ElementTree(xdxf)
    ET.indent(output_tree, space="  ")
    output_tree.write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"Successfully converted [{lang_from} -> {lang_to}]: {tmx_path} -> {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tmx2xdxf.py <input.tmx> <output.xdxf>")
        sys.exit(1)

    tmx_input = sys.argv[1]
    xdxf_output = sys.argv[2]
    
    tmx_to_xdxf_dynamic(tmx_input, xdxf_output)