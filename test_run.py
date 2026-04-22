import os
import requests
from pympi.Elan import Eaf

# Config
EAF_DIR = "eaf_output" # Make sure this matches your folder name!
SERVER_URL = "http://127.0.0.1:8080/completion"

def test_connection():
    try:
        response = requests.post(SERVER_URL, json={"prompt": "test", "n_predict": 1}, timeout=5)
        return response.status_code == 200
    except:
        return False

print(f"📡 Checking server...")
if test_connection():
    print("✅ Server is ALIVE.")
else:
    print("❌ Server is NOT responding. Check Terminal 1.")
    exit()

print(f"📂 Checking folder: {os.path.abspath(EAF_DIR)}")
if not os.path.exists(EAF_DIR):
    print(f"❌ Folder '{EAF_DIR}' not found!")
    exit()

files = [f for f in os.listdir(EAF_DIR) if f.endswith('.eaf')]
print(f"📄 Found {len(files)} EAF files.")

for filename in files[:3]: # Just test the first 3
    path = os.path.join(EAF_DIR, filename)
    eaf = Eaf(path)
    tiers = eaf.get_tier_names()
    print(f"\n🔍 File: {filename}")
    print(f"   Tiers found: {', '.join(tiers)}")
    
    if "Transcription-MIA" in tiers:
        anns = eaf.get_annotation_data_for_tier("Transcription-MIA")
        if anns:
            print(f"   ✨ Text found: '{anns[0][2]}'")
        else:
            print("   ⚠️ Tier exists but is EMPTY.")
    else:
        print("   ❌ 'Transcription-MIA' tier NOT found in this file.")