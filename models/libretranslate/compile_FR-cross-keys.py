# compile_FR-cross-keys.py
import time
import os
import torch
import pandas as pd
from transformers import pipeline
from libretranslatepy import LibreTranslateAPI

# --- CONFIGURATION ---
HISTORICAL_FR_INPUT = "train-historical_fr"  # Ensure this file is inside c:\tools\ModFr-Norm
CSV_OUT = "myaamia_normalized_crosskeys.csv"

# Local translation engine parameters (safe chunk sizes for aged hardware)
lt = LibreTranslateAPI("http://localhost:5000")
LT_BATCH_SIZE = 50
LT_COOLDOWN = 1.0

# 1. VERIFY OR CREATE AN INPUT DATA STREAM FILE
if not os.path.exists(HISTORICAL_FR_INPUT):
    print(f"Creating a sample '{HISTORICAL_FR_INPUT}' file for validation...")
    with open(HISTORICAL_FR_INPUT, "w", encoding="utf-8") as f:
        f.write("Elle haïſſoit particulierement le Cardinal de Lorraine;\n")
        f.write("Adieu, i'iray chez vous tantoſt vous rendre grace.\n")

# 2. INITIALIZE HUGGING FACE NORMALIZATION PIPELINE ON GPU
print("Loading ModFr-Norm pipeline onto global GPU context...")
# NOTE: Removed cache_file parameter to ensure stable execution on Python 3.14+
normaliser = pipeline(
    model="rbawden/modern_french_normalisation", 
    batch_size=32, 
    beam_size=5, 
    trust_remote_code=True,
    device=0  # Directs processing straight to your active CUDA environment
)

# --- STAGE A: GPU-ACCELERATED TEXT NORMALIZATION ---
print(f"Reading historical lines from: {os.path.abspath(HISTORICAL_FR_INPUT)}")
with open(HISTORICAL_FR_INPUT, "r", encoding="utf-8") as f:
    historical_lines = [line.strip() for line in f if line.strip()]

print(f"Normalizing {len(historical_lines)} lines on CUDA...")
start_time = time.time()

pipeline_outputs = normaliser(historical_lines)
modern_fr_lines = [output['text'] for output in pipeline_outputs]

print(f"Normalization complete in {time.time() - start_time:.2f} seconds.")

# --- STAGE B: CONTROLLED CHUNKED TRANSLATION ---
print(f"Translating modern keys into English (Safe chunks of {LT_BATCH_SIZE})...")
total_lines = len(modern_fr_lines)
english_lines = []

for i in range(0, total_lines, LT_BATCH_SIZE):
    chunk_modern = modern_fr_lines[i:i + LT_BATCH_SIZE]
    
    try:
        chunk_en = lt.translate(chunk_modern, "fr", "en")
        if isinstance(chunk_en, str):
            chunk_en = [chunk_en]
    except Exception as e:
        print(f"Throttling connection block at row {i}. Falling back to single strings...")
        chunk_en = []
        for item in chunk_modern:
            try:
                chunk_en.append(lt.translate(item, "fr", "en"))
            except:
                chunk_en.append("[TRANSLATION_FAILED]")
                
    english_lines.extend(chunk_en)
    print(f"Progress: Completed batch {i} to {min(i + LT_BATCH_SIZE, total_lines)}/{total_lines}")
    time.sleep(LT_COOLDOWN)

# --- STAGE C: STRUCTURED CSV EXPORT ---
print("Compiling alignments into unified Pandas DataFrame...")

# Pad out arrays if any translation fallback entries missed structural loops
if len(english_lines) < len(historical_lines):
    english_lines += ["[MISSING]"] * (len(historical_lines) - len(english_lines))

dataset_dict = {
    "historical_fr": historical_lines,
    "modern_fr": modern_fr_lines,
    "en": english_lines[:len(historical_lines)]
}

df = pd.DataFrame(dataset_dict)

# Force strict UTF-8 to keep French diacritics pristine in Windows environments
df.to_csv(CSV_OUT, index=False, encoding="utf-8")
print(f"Success! Cross keys compiled at: {os.path.abspath(CSV_OUT)}")
