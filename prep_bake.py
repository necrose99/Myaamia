import pandas as pd
import json

def create_training_data(csv_path, output_jsonl):
    # Load your sanitized CSV
    df = pd.read_csv(csv_path)
    
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            # Entry 1: Translation Task
            item_en = {
                "instruction": "Translate the Myaamia word to English.",
                "input": row['mia_citation'],
                "output": row['en']
            }
            f.write(json.dumps(item_en) + '\n')
            
            # Entry 2: Linguistic Form Task
            item_stem = {
                "instruction": "Identify the stem for the following Myaamia citation form.",
                "input": row['mia_citation'],
                "output": row['mia_stem']
            }
            f.write(json.dumps(item_stem) + '\n')

    print(f"✅ Created {output_jsonl} with {len(df)*2} training examples.")

if __name__ == "__main__":
    create_training_data('ilda_full.csv', 'mia_train.jsonl')