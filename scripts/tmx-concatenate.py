import xml.etree.ElementTree as ET
import glob
import os
from datetime import datetime, timezone

def repair_encoding(text):
    """Simple fix for common UTF-8 to Windows-1252 artifacts."""
    if not text: return ""
    # Add common repairs here if you see specific artifacts
    repairs = {
        "Å¡": "š",
        "Å": "ą", 
        "ii": "ii", # placeholder for logic if needed
    }
    for bad, good in repairs.items():
        text = text.replace(bad, good)
    return text

def final_unified_merge():
    output_file = 'Algic_Unified_Master.tmx'
    ET.register_namespace('xml', "http://www.w3.org/XML/1998/namespace")
    
    root = ET.Element("tmx", version="1.4")
    header = ET.SubElement(root, "header", {
        "creationtool": "Algic-Unified-Merger",
        "datatype": "PlainText",
        "segtype": "phrase",
        "srclang": "en-US",
        "creationdate": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    })
    body = ET.SubElement(root, "body")

    master_data = {}
    files = [f for f in glob.glob("*.tmx") if f != output_file]

    for file_path in files:
        try:
            tree = ET.parse(file_path)
            for tu in tree.findall(".//tu"):
                temp_langs = {}
                for tuv in tu.findall(".//tuv"):
                    # Extract lang and normalize specifically to en-US
                    lang_attr = [v for k, v in tuv.attrib.items() if k.endswith('lang')][0].lower()
                    norm_lang = 'en-US' if lang_attr.startswith('en') else lang_attr
                    
                    seg_node = tuv.find(".//seg")
                    if seg_node is not None and seg_node.text:
                        clean_text = repair_encoding(seg_node.text.strip())
                        if clean_text:
                            temp_langs[norm_lang] = clean_text

                # Use en-US as key, or fallback to the first available lang (for scientific/arcane)
                primary_key = temp_langs.get('en-US') or next(iter(temp_langs.values()), None)

                # Skip placeholders or empty units
                if not primary_key or "[Placeholder" in primary_key:
                    continue

                if primary_key not in master_data:
                    master_data[primary_key] = {}
                
                master_data[primary_key].update(temp_langs)

        except Exception as e:
            print(f"❌ Error in {file_path}: {e}")

    # Rebuild sorted XML
    for i, (concept, translations) in enumerate(sorted(master_data.items())):
        tu_node = ET.SubElement(body, "tu", tuid=f"alg_{i:06d}")
        for lang, text in translations.items():
            tuv_node = ET.SubElement(tu_node, "tuv")
            tuv_node.set("{http://www.w3.org/XML/1998/namespace}lang", lang)
            ET.SubElement(tuv_node, "seg").text = text

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"✅ Successfully merged {len(master_data)} concepts into {output_file}")

if __name__ == "__main__":
    final_unified_merge()