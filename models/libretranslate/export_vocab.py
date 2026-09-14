import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
tokenizer_path = os.path.join(base_dir, "myaamia_tokenizer.json")
output_vocab_path = os.path.join(base_dir, "model", "vocabulary.json")

# Extract the sorted vocabulary keys list from Hugging Face
with open(tokenizer_path, "r", encoding="utf-8") as f:
    data = json.load(f)

vocab_list = list(data["model"]["vocab"].keys())

os.makedirs(os.path.dirname(output_vocab_path), exist_ok=True)
with open(output_vocab_path, "w", encoding="utf-8") as f:
    json.dump(vocab_list, f, indent=4, ensure_ascii=False)

print(f"[+] Successfully exported vocabulary.json for compile script!")
