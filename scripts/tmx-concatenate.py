import xml.etree.ElementTree as ET
import glob
import os
import datetime

def concatenate_tmx(input_folder, output_file):
    # 1. Setup Master TMX Root
    master_tmx = ET.Element("tmx", version="1.4")
    header = ET.SubElement(master_tmx, "header", {
        "creationtool": "Algic-Concatenator",
        "creationtoolversion": "1.0",
        "segtype": "phrase",
        "adminlang": "en-US",
        "srclang": "en-US",
        "datatype": "PlainText",
        "creationdate": datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
    })
    body = ET.SubElement(master_tmx, "body")

    # 2. Track UIDs to prevent duplicates
    seen_tuids = set()
    total_files = 0

    # 3. Iterate through all .tmx files in the folder
    for tmx_file in glob.glob(os.path.join(input_folder, "*.tmx")):
        if os.path.abspath(tmx_file) == os.path.abspath(output_file):
            continue
            
        print(f"📦 Processing {tmx_file}...")
        tree = ET.parse(tmx_file)
        root = tree.getroot()
        
        for tu in root.findall(".//tu"):
            tuid = tu.get("tuid")
            
            # If TUID is missing or duplicate, generate a unique one
            if not tuid or tuid in seen_tuids:
                tuid = f"gen_{datetime.datetime.now().microsecond}_{len(seen_tuids)}"
                tu.set("tuid", tuid)
            
            seen_tuids.add(tuid)
            body.append(tu)
        
        total_files += 1

    # 4. Write Master File
    tree = ET.ElementTree(master_tmx)
    ET.indent(tree, space="  ", level=0) # Pretty print
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    
    print(f"\n✅ Concatenation Complete!")
    print(f"📁 Merged {total_files} files into {output_file}")
    print(f"🔢 Total Translation Units: {len(seen_tuids)}")

if __name__ == "__main__":
    # Create an 'imports' folder and dump your TMX files there
    concatenate_tmx('imports/', 'Algic_Master.tmx')
