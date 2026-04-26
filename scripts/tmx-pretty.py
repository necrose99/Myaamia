import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import os
from pathlib import Path

def polish_tmx_stash(stash_dir):
    path = Path(stash_dir)
    tmx_files = list(path.glob("*.tmx"))
    
    print(f"🛰️  Scanning {len(tmx_files)} files for one-liners and typos...")

    for tmx_file in tmx_files:
        temp_file = tmx_file.with_suffix(".tmx.tmp")
        
        try:
            # 1. READ & REPAIR
            with open(tmx_file, "r", encoding="utf-8") as f:
                raw_text = f.read()

            # Fix the common typos that break the parser
            raw_text = raw_text.replace("</propr>", "</prop>").replace("</propre>", "</prop>")
            # Fix raw ampersands that web services often miss
            raw_text = re.sub(r"&(?!(amp|lt|gt|apos|quot);)", "&amp;", raw_text)

            # 2. PARSE & SORT TAGS
            root = ET.fromstring(raw_text)
            for tu in root.findall(".//tu"):
                # Grab children to re-order them
                props = tu.findall("prop")
                tuvs = tu.findall("tuv")
                notes = tu.findall("note")

                # Sort Props by type (e.g., x-author, x-isbn)
                props.sort(key=lambda x: x.get("type", ""))

                # Clear and Re-weld in readable order
                for child in list(tu):
                    tu.remove(child)
                tu.extend(notes) # Notes first
                tu.extend(props) # Bibilio data second
                tu.extend(tuvs)  # Word segments last

            # 3. PRETTY PRINT (No more one-liners)
            rough_string = ET.tostring(root, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            
            # Filter blank lines that minidom sometimes adds
            pretty_xml = "\n".join([line for line in reparsed.toprettyxml(indent="  ").splitlines() if line.strip()])

            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(pretty_xml)

            # 4. SWAP
            os.replace(temp_file, tmx_file)
            print(f"✅ Polished: {tmx_file.name}")

        except Exception as e:
            if temp_file.exists(): temp_file.unlink()
            print(f"❌ Failed to repair {tmx_file.name}: {e}")

if __name__ == "__main__":
    # Point this to your Myaamia/data_shards directory
    polish_tmx_stash(r"C:\Users\black\GitHub\Myaamia\data_shards\tmx")