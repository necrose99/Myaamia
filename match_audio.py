from faster_whisper import WhisperModel
import os
import pandas as pd
import shutil
from rapidfuzz import process, utils
import json
import sys

# FORCE UTF-8 for the terminal to prevent the 'charmap' crash
sys.stdout.reconfigure(encoding='utf-8')

# Define your output file
LOG_JSON = "match_results.jsonl" 

def log_to_json(data):
    with open(LOG_JSON, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
        
# 1. Configuration & Data Loading
GOLD_CSV = "myaamia_gold_standard.csv"
AUDIO_DIR = r"C:\Users\black\GitHub\Myaamia\corpus_media\full"
OUTPUT_DIR = r"C:\Users\black\GitHub\Myaamia\corpus_media\identified"

if not os.path.exists(GOLD_CSV):
    print(f"Error: {GOLD_CSV} not found!")
    exit()

df = pd.read_csv(GOLD_CSV)
# Use the column name from your CSV ('myaamia')
dictionary = df['myaamia'].dropna().tolist()
myaamia_context = ", ".join(dictionary[:50])

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 2. Initialize Model (Stick to CPU/Int8 for the HP Envy)
print("Loading Whisper Model on CPU...")
model = WhisperModel("tiny", device="cpu", compute_type="int8")

print(f"Listening to files in {AUDIO_DIR}...")

# 3. Processing Loop
for mp3 in os.listdir(AUDIO_DIR):
    if mp3.endswith(".mp3"):
        mp3_path = os.path.join(AUDIO_DIR, mp3)
        
        try:
            segments, _ = model.transcribe(
                mp3_path, 
                language="en", # English base helps catch phonetics
                initial_prompt=f"Myaamia words like: {myaamia_context}",
                beam_size=5
            )
            
            text_guess = "".join([s.text for s in segments]).lower().strip()
            clean_guess = "".join(e for e in text_guess if e.isalpha())
            
            if len(clean_guess) < 3: 
                continue 

            # FUZZY MATCHING (Connecting Heard to Gold)
            # This finds the closest match in your myaamia_gold_standard.csv
            best_match = process.extractOne(clean_guess, dictionary, processor=utils.default_process)
            
            if best_match:
                matched_word, confidence, index = best_match
                
                result = {
                    "file": mp3,
                    "heard": clean_guess,
                    "matched": matched_word,
                    "confidence": confidence
                }
                
                log_to_json(result)
                
                # Only move the file if it's a "Gold" match (e.g., > 85%)
                if confidence > 85:
                    shutil.copy(mp3_path, os.path.join(OUTPUT_DIR, f"{matched_word}_{mp3}"))
                    print(f"Matched: {mp3} -> {matched_word} ({confidence}%)")
                else:
                    print(f"Low Confidence: {mp3} heard {clean_guess}")

        except Exception as e:
            print(f"Error processing {mp3}: {e}")