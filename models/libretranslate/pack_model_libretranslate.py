#!/usr/bin/env python3
import os
import json
import zipfile

def create_model_package(target_dir, output_filename="en_mia.argosmodel"):
    """Validates the bare model workspace directory and packages it into an .argosmodel archive."""
    # 1. Ensure absolute paths are evaluated correctly
    target_dir = os.path.abspath(target_dir)
    model_dir = os.path.join(target_dir, "model")
    
    # 2. Structural safety checks
    if not os.path.exists(target_dir):
        print(f"[!] Error: Target directory {target_dir} does not exist.")
        return
        
    print(f"[-] Packaging workspace assets from: {target_dir}")
    
    # 3. Dynamic verification of mandatory translation parameters
    required_files = ["metadata.json", "sentencepiece.model"]
    missing = [f for f in required_files if not os.path.exists(os.path.join(target_dir, f))]
    
    if missing:
        print(f"[!] Warning: Missing critical deployment components in core directory: {missing}")
        
    if not os.path.exists(model_dir):
        print("[!] Warning: 'model/' weight directory stub is missing.")

    # 4. Generate the compressed package asset
    output_path = os.path.join(os.path.dirname(target_dir), output_filename)
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                # Omit pre-existing model archives from recursive wrapping loops
                if file.endswith('.argosmodel'):
                    continue
                file_path = os.path.join(root, file)
                # Compute relative paths inside the archive layer
                arc_name = os.path.relpath(file_path, target_dir)
                zipf.write(file_path, arc_name)
                
    print(f"[+] Model deployment package successfully generated:\n    -> {output_path}")

# Local orchestration execution:
if __name__ == "__main__":
    workspace = r"C:\Users\black\GitHub\Myaamia\models\libretranslate"
    create_model_package(workspace)

