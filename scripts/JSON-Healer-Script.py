import re
import json
import os

def brute_force_recovery(input_path, output_path):
    print(f"🛠️  Brute-forcing recovery on {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find individual JSON objects: {"iso": ... }
    # This ignores missing commas or broken array brackets
    pattern = re.compile(r'\{"iso":.*?"status":\s*".*?"\}', re.DOTALL)
    matches = pattern.findall(content)

    recovered_data = []
    for m in matches:
        try:
            recovered_data.append(json.loads(m))
        except:
            continue

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recovered_data, f, indent=2)
    
    print(f"✅ Recovered {len(recovered_data)} valid objects.")
    print(f"💾 Saved to {output_path}")

if __name__ == "__main__":
    json_raw = os.path.join("scripts", "mirror_results.json")
    json_fixed = os.path.join("scripts", "mirror_results_FIXED.json")
    brute_force_recovery(json_raw, json_fixed)