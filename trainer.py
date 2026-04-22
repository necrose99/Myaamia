import xml.etree.ElementTree as ET
import json

# Settings
tmx_file = r"C:\Users\black\GitHub\Myaamia\ilda_full.tmx"
output_file = r"C:\Users\black\GitHub\Myaamia\training_data.jsonl"
src_lang = "en"  # Update to your source lang code
tgt_lang = "mia" # Update to your target lang code (e.g., Myaamia)

def convert_tmx_to_jsonl(tmx_path, out_path):
    tree = ET.parse(tmx_path)
    root = tree.getroot()
    
    with open(out_path, 'w', encoding='utf-8') as f:
        for tu in root.findall(".//tu"):
            res = {}
            for tuv in tu.findall("tuv"):
                lang = tuv.get("{http://w3.org}lang")
                text = tuv.find("seg").text
                if lang == src_lang: res['instruction'] = f"Translate to Myaamia: {text}"
                if lang == tgt_lang: res['output'] = text
            
            if 'instruction' in res and 'output' in res:
                f.write(json.dumps(res, ensure_ascii=False) + '\n')

convert_tmx_to_jsonl(tmx_file, output_file)
print(f"Direct conversion finished: {output_file}")
