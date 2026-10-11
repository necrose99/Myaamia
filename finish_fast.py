import pandas as pd
from deep_translator import GoogleTranslator
import time

input_file = "ilda_full.csv"
output_file = "ilda_full.csv"

df = pd.read_csv(input_file)
translator = GoogleTranslator(source='en', target='fr')

total = len(df)
print(f"Resuming translation from row 560 to {total} with rate-limiting...")

# Google allows ~5 requests/sec max, so a 0.25s pause keeps us safely under that threshold
DELAY_BETWEEN_REQUESTS = 0.25  # 250ms per item (~4 requests/sec max)

for idx, row in df.iterrows():
    # Skip already translated rows
    if pd.notna(row['fr']) and str(row['fr']).strip():
        continue

    text = str(row['en-us']) if pd.notna(row['en-us']) else ""
    if not text.strip():
        continue

    try:
        translated = translator.translate(text)
        df.at[idx, 'fr'] = translated
        df.at[idx, 'fro'] = translated
        time.sleep(DELAY_BETWEEN_REQUESTS)
    except Exception as e:
        print(f"Rate limit or network error at row {idx}: {e}")
        print("Cooling down for 10 seconds before retrying...")
        time.sleep(10)

    # Save progress every 50 rows
    if (idx + 1) % 50 == 0 or (idx + 1) == total:
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        completed = df['fr'].notnull().sum()
        print(f"Checkpoint saved: {completed} / {total} rows finished ({(completed/total)*100:.1f}%)")

df.to_csv(output_file, index=False, encoding="utf-8-sig")
print("Complete! ilda_full.csv is ready for training.")