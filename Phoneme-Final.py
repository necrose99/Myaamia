import os
import requests
import json
from pympi.Elan import Eaf

# Configuration
EAF_DIR = "eaf_output"
SERVER_URL = "http://127.0.0.1:8080/completion"

SYSTEM_PROMPT = (
    "You are a Myaamia language linguist. Provide ONLY the IPA phonemes for the word. "
    "Rules: š=/ʃ/, aa=/aː/, ee=/eː/, ii=/iː/, oo=/oː/, hk=/ʰk/, ht=/ʰt/, hp=/ʰp/. "
    "Do not explain. Do not repeat the word. Output only the IPA."
)

def get_ipa(word):
    # Forcing the assistant to start with '/' helps prevent chatter
    prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{SYSTEM_PROMPT}<|eot_id|><|start_header_id|>user<|end_header_id|>\n{word}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n/"
    
    payload = {
        "prompt": prompt,
        "n_predict": 32,
        "temperature": 0.05,
        "stop": ["<|eot_id|>", "\n", "-", ">"]
    }
    try:
        response = requests.post(SERVER_URL, json=payload, timeout=30)
        content = response.json()['content'].strip().split('/')[0].strip()
        if not content or content == word:
            return "/processing_fail/"
        return f"/{content}/"
    except Exception:
        return "/timeout_error/"

def run_production():
    files = [f for f in os.listdir(EAF_DIR) if f.endswith('.eaf')]
    print(f"🚀 Processing {len(files)} files...")

    for filename in files:
        path = os.path.join(EAF_DIR, filename)
        eaf = Eaf(path)
        
        # --- SKIP LOGIC START ---
        # Only process files that are empty, botched (short), or errors
        current_anns = eaf.get_annotation_data_for_tier("Phoneme-MIA")
        if current_anns:
            val = current_anns[0][2]
            if len(val) > 3 and "error" not in val and "fail" not in val:
                print(f"⏭️  {filename} is already good. Skipping.")
                continue
        # --- SKIP LOGIC END ---

        anns = eaf.get_annotation_data_for_tier("Transcription-MIA")
        if not anns: continue
        
        word = anns[0][2]
        print(f"🧠 {word}...", end=" ", flush=True)
        
        ipa_val = get_ipa(word)
        start, end = anns[0][0], anns[0][1]
        
        eaf.remove_all_annotations_from_tier("Phoneme-MIA")
        eaf.add_annotation("Phoneme-MIA", start, end, ipa_val)
        
        # Prevent Windows .bak collision
        bak_path = path.replace(".eaf", ".bak")
        if os.path.exists(bak_path):
            os.remove(bak_path)
            
        eaf.to_file(path)
        print(f"✅ {ipa_val}")

if __name__ == "__main__":
    run_production()