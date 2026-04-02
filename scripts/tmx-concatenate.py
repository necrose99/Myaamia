import xml.etree.ElementTree as ET
import glob
import os
import datetime

def merge_tmx_shards(input_folder, output_file):
    # 1. Setup Master TMX Structure
    master_tmx = ET.Element("tmx", version="1.4")
    header = ET.SubElement(master_tmx, "header", {
        "creationtool": "Algic-Merge-Master",
        "creationtoolversion": "2.0",
        "segtype": "phrase",
        "adminlang": "en-US",
        "srclang": "en-US",
        "datatype": "PlainText"
    })
    body = ET.SubElement(master_tmx, "body")

    # 2. Storage for Merging: { "English Segment": TU_Element }
    master_map = {}

    # Namespace handling
    ns = {'xml': 'http://www.w3.org/XML/1998/namespace'}

    for tmx_file in glob.glob(os.path.join(input_folder, "*.tmx")):
        if os.path.abspath(tmx_file) == os.path.abspath(output_file):
            continue
            
        print(f"🔗 Merging shard: {tmx_file}")
        tree = ET.parse(tmx_file)
        
        for tu in tree.findall(".//tu"):
            # Find the English Source segment to use as a Key
            en_seg_el = tu.find(".//tuv[@xml:lang='en-US']/seg", ns)
            if en_seg_el is None or not en_seg_el.text:
                continue
            
            en_key = en_seg_el.text.strip()

            if en_key not in master_map:
                # First time seeing this concept, add the whole TU
                new_tu = ET.Element("tu", tuid=f"alg_{len(master_map):05d}")
                # Copy existing TUVs
                for tuv in tu.findall("tuv"):
                    new_tu.append(tuv)
                master_map[en_key] = new_tu
                body.append(new_tu)
            else:
                # Concept exists, merge new language variants (TUVs) into it
                existing_tu = master_map[en_key]
                existing_langs = [tuv.get(f"{{{ns['xml']}}}lang") for tuv in existing_tu.findall("tuv")]
                
                for tuv in tu.findall("tuv"):
                    lang = tuv.get(f"{{{ns['xml']}}}lang")
                    if lang not in existing_langs:
                        existing_tu.append(tuv)

    # 3. Save the Master TMX
    tree = ET.ElementTree(master_tmx)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    
    print(f"\n✅ Master Merge Complete: {output_file}")
    print(f"📊 Total Unique Concepts (Rows): {len(master_map)}")

if __name__ == "__main__":
    merge_tmx_shards('imports/', 'Algic_Master.tmx')
