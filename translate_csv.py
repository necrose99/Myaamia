import pandas as pd
import requests
import time

input_file = "ilda_full.csv"
output_file = "ilda_full.csv"
api_url = "http://127.0.0.1:5050/translate"

print(f"Reading {input_file}...")
df = pd.read_csv(input_file)

# Ensure columns exist
for col in ['fr', 'fro']:
    if col not in df.columns:
        df[col] = ""

total = len(df)
print(f"Starting batch processing of {total} rows via local Gemma 3 CPU engine...")

# Process row-by-row with progress logging and auto-save
for idx, row in df.iterrows():
    # Skip if already translated
    if pd.notna(row['fr']) and str(row['fr']).strip():
        continue

    text = str(row['en-us']) if pd.notna(row['en-us']) else ""
    if not text.strip():
        continue

    payload = {
        "q": text,
        "source": "en",
        "target": "fr",
        "format": "text",
        "api_key": ""
    }

    try:
        res = requests.post(api_url, json=payload, timeout=30)
        if res.status_code == 200:
            translated = res.json().get("translatedText", "").strip()
            df.at[idx, 'fr'] = translated
            df.at[idx, 'fro'] = translated
        else:
            print(f"Error at row {idx}: HTTP {res.status_code}")
    except Exception as e:
        print(f"Timeout/Error at row {idx}: {e}")
        time.sleep(1)

    # Save progress every 20 rows so work is not lost
    if (idx + 1) % 20 == 0 or (idx + 1) == total:
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"Saved progress: {idx + 1} / {total} rows processed.")

print("Translation complete! Updated ilda_full.csv.")