import os
import json

# Path to your webcorpus
BASE_CORPUS = r"C:\Users\black\GitHub\Myaamia\webcorpus"
IDENTIFIED_DIR = r"C:\Users\black\GitHub\Myaamia\corpus_media\identified"
OUTPUT_FILE = "universal_shard_manifest.json"

def build_universal_map():
    manifest = {
        "primary_myaamia": [],
        "cousin_data": {},
        "metadata_blobs": []
    }

    print("🛰️ Scanning Webcorpus Shards...")
    
    for root, dirs, files in os.walk(BASE_CORPUS):
        shard_name = os.path.basename(root)
        
        # Track which language we are looking at
        current_lang = "unknown"
        if "ojibwe" in root.lower(): current_lang = "ojibwe"
        elif "potawatomi" in root.lower(): current_lang = "potawatomi"
        elif "sauk" in root.lower(): current_lang = "sauk"
        elif "lenape" in root.lower(): current_lang = "lenape"

        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            
            # Index structured data (JSON, XML, MHTML)
            if file_ext in ['.json', '.xml', '.mhtml', '.html']:
                entry = {
                    "shard": shard_name,
                    "language": current_lang,
                    "file": file,
                    "path": os.path.join(root, file)
                }
                
                if current_lang not in manifest["cousin_data"]:
                    manifest["cousin_data"][current_lang] = []
                manifest["cousin_data"][current_lang].append(entry)

    # Save the manifest
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created manifest with {len(manifest['cousin_data'])} language shards indexed.")

if __name__ == "__main__":
    build_universal_map()