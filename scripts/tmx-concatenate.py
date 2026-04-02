import xml.etree.ElementTree as ET
import glob
import os
from datetime import datetime

def master_tmx_merge(input_dir, output_file):
    # 1. Initialize the Master TMX Structure
    now = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    root = ET.Element("tmx", version="1.4")
    header = ET.SubElement(root, "header", {
        "creationtool": "Algic-Master-Merge",
        "creationtoolversion": "2.0",
        "segtype": "phrase",
        "adminlang": "en-US",
        "srclang": "en-US",
        "datatype": "PlainText",
        "creationdate": now
    })
    body = ET.SubElement(root, "body")

    # 2. Concept Map: { "English Segment": TU_Element }
    # This deduplicates by concept rather than just smashing files together.
    master_map = {}
    ns = {'xml': 'http://www.w3.org/XML/1998/namespace'}

    # 3. Process every TMX in the shard directory
    tmx_files = glob.glob(os.path.join(input_dir, "*.tmx"))
    print(f"🧹 Cleaning and merging {len(tmx_files)} shards...")

    for file_path in tmx_files:
        try:
            tree = ET.parse(file_path)
            shard_root = tree.getroot()
            
            for tu in shard_root.findall(".//tu"):
                # Find the English reference (The Key)
                en_tuv = tu.find("./tuv[@xml:lang='en-US']", ns)
                if en_tuv is None:
                    # Fallback: check for 'en' or other English variants
                    en_tuv = tu.find("./tuv[@xml:lang='en']", ns)
                
                if en_tuv is not None:
                    en_seg = en_tuv.find("seg").text.strip()
                    
                    if en_seg not in master_map:
                        # New Concept: Create the "Master Row"
                        new_tu = ET.Element("tu", tuid=f"alg_{len(master_map):06d}")
                        for tuv in tu.findall("tuv"):
                            new_tu.append(tuv)
                        master_map[en_seg] = new_tu
                        body.append(new_tu)
                    else:
                        # Existing Concept: Merge unique language columns (tuv)
                        existing_tu = master_map[en_seg]
                        existing_langs = [t.get(f"{{{ns['xml']}}}lang") for t in existing_tu.findall("tuv")]
                        
                        for tuv in tu.findall("tuv"):
                            lang = tuv.get(f"{{{ns['xml']}}}lang")
                            if lang not in existing_langs:
                                existing_tu.append(tuv)
        except Exception as e:
            print(f"⚠️ Skipping broken shard {file_path}: {e}")

    # 4. Final Polish: Indentation and Writing
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    
    print(f"✅ DONE. Master file '{output_file}' is ready for SQL import.")
    print(f"📊 Unique Algic Concepts: {len(master_map)}")

if __name__ == "__main__":
    # Put all your 'numbers.tmx', 'sauk_workbook.tmx', 'omniglot.tmx' here
    master_tmx_merge('shards/', 'Algic_Master_Final.tmx')
