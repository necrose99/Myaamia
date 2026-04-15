import os
import re

def repair_myaamia_tmx(input_path):
    output_path = f"repaired_{os.path.basename(input_path)}"
    
    # Specific mappings for the snippets provided:
    # Å¡ -> š
    # Å’ -> Š
    # Note: \xaa and \x9a are the raw hex variants often hit by wildcards
    replacements = {
        r'Å¡': 'š',
        r'Å¡': 'š',
        r'Å’': 'Š',
        r'Å½': 'Ž',
    }

    try:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # 1. Targeted Replacement for known Å sequences
        for artifact, correction in replacements.items():
            content = re.sub(artifact, correction, content)

        # 2. Wildcard Cleanup: Fixes "Å" followed by any non-XML char
        # This catches stray variants like Å followed by a space or scrambled bit
        content = re.sub(r'Å[^\s<]{1}', 'š', content)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ Success! Repaired: {output_path}")
        print(f"Sample Fix: aÅ¡iihkionam- -> ašiihkionam-")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Get all .tmx files in the current directory
    tmx_files = [f for f in os.listdir('.') if f.lower().endswith('.tmx')]
    
    if not tmx_files:
        print("No .tmx files found in this folder.")
    else:
        print("Found TMX files:", tmx_files)
        choice = input("Repair [A]ll or [S]ingle file? ").strip().lower()
        
        if choice == 'a':
            for f in tmx_files:
                repair_myaamia_tmx(f)
        else:
            file_to_fix = input("Enter the specific filename: ").strip()
            if os.path.exists(file_to_fix):
                repair_myaamia_tmx(file_to_fix)
            else:
                print("File not found.")


