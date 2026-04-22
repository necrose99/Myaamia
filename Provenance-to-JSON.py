import os
import json

BASE_CORPUS = r"C:\Users\black\GitHub\Myaamia\webcorpus"
IDENTIFIED_DIR = r"C:\Users\black\GitHub\Myaamia\corpus_media\identified"
OUTPUT_JSON = "provenance_master_map.json"

def get_origin_url(folder_path):
    origin_file = os.path.join(folder_path, "webcopy-origin.txt")
    if os.path.exists(origin_file):
        with open(origin_file, 'r', encoding='utf-8', errors='ignore') as f:
            return f.readline().strip() # Usually the first line is the URL
    return "Unknown Source"

def build_map():
    provenance_map = {}
    
    print("🔍 Mapping Shard Origins...")
    # Walk through webcorpus to map folder names to URLs
    for root, dirs, files in os.walk(BASE_CORPUS):
        if "webcopy-origin.txt" in files:
            folder_name = os.path.basename(root)
            provenance_map[folder_name] = get_origin_url(root)

    # Now map identified files
    final_data = []
    print("📑 Linking Identified Audio to Sources...")
    for filename in os.listdir(IDENTIFIED_DIR):
        if filename.endswith(".mp3"):
            # Logic: If the filename contains a hash, we can potentially 
            # find which shard it belongs to by looking for that hash in the webcorpus
            source_shard = "Myaamia Gold" # Default
            for shard, url in provenance_map.items():
                if shard.lower() in filename.lower():
                    source_shard = url
                    break

            final_data.append({
                "file": filename,
                "origin_url": source_shard,
                "stem": filename.split('-')[0]
            })

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created {OUTPUT_JSON} with {len(final_data)} entries.")

if __name__ == "__main__":
    build_map()