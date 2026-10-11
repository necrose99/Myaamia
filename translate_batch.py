import pandas as pd
import requests
import json
import time

input_file = "ilda_full.csv"
output_file = "ilda_full_fr.csv"  
api_url = "http://127.0.0"
batch_size = 50  # Size of one batch

print(f"Reading file {input_file}...")
df = pd.read_csv(input_file)

translated_fr = []
total_rows = len(df)

print(f"Total rows in table: {total_rows}. Proceeding with translation...")

# Row-by-row loop with clean structural pairing
for idx, row in df.iterrows():
    text_to_translate = str(row['en-us']) if pd.notna(row['en-us']) else ""
    
    if text_to_translate.strip():
        payload = {
            "q": text_to_translate,
            "source": "en",  # Use "en" on LibreTranslate
            "target": "fr",
            "format": "text",
            "api_key": "1"
        }
        try:
            response = requests.post(api_url, json=payload, headers={"Content-Type": "application/json"}, timeout=5)
            if response.status_code == 200:
                translated_fr.append(response.json().get("translatedText", ""))
            else:
                translated_fr.append("")
        except Exception as e:
            translated_fr.append("")
    else:
        translated_fr.append("")

    # Display batch notification on the terminal (Every 50 rows)
    processed = idx + 1
    if processed % batch_size == 0 or processed == total_rows:
        print(f"[BATCH NOTIFICATION] Processed: {processed} / {total_rows} ({(processed/total_rows)*100:.1f}%)")

# Insert 'fr' and 'fro' columns into the dataframe
df['fr'] = translated_fr
df['fro'] = translated_fr

# Save to CSV
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"Job completed successfully! {output_file} has been updated.")
