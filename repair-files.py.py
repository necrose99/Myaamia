#!/bin/python3 
#repair-files.py
### repair UTF8 file scrambles on scraping of chairs... 


import os
import re

def repair_linguistic_file(input_path):
    # Mapping common UTF-8 artifacts found in Myaamia/Algonquian data
    # Add more mappings here if you find other corrupted characters
    replacements = {
        "Å¡": "š",
        "Å’": "Š",
        "Ã¡": "á",
        "Ã©": "é",
        "Ã­": "í",
        "Ã³": "ó",
        "Ãº": "ú",
        "Ã±": "ñ",
        "Ã": "à", # Use cautiously, can be part of other chars
    }

    output_path = f"repaired_{os.path.basename(input_path)}"

    try:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Perform replacements
        for artifact, correction in replacements.items():
            content = content.replace(artifact, correction)

        # Optional: Clean up malformed SFM markers if necessary
        # content = re.sub(r'\\lx\s+', r'\lx ', content)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Success! Repaired file saved as: {output_path}")

    except Exception as e:
        print(f"❌ Error processing file: {e}")

if __name__ == "__main__":
    file_to_fix = input("Enter the filename (e.g., data.sfm): ").strip()
    if os.path.exists(file_to_fix):
        repair_linguistic_file(file_to_fix)
    else:
        print("File not found.")