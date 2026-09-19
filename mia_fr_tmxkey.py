import xml.etree.ElementTree as ET
import re
from libretranslatepy import LibreTranslateAPI

# Initialize your lightweight local engine
LT_URL = "http://localhost:5000"
lt_client = LibreTranslateAPI(LT_URL)

def basic_fro_transformer(modern_fr: str) -> str:
    """
    Lightweight rule-based fallback for old orthography 
    when running on resource-constrained devices without heavy models.
    """
    text = modern_fr.lower().strip()
    # Apply standard 1700s script changes
    text = text.replace("les", "leſ").replace("des", "deſ")
    text = re.sub(r'\boui\b', 'ovÿ', text)
    text = re.sub(r'\bparlait\b', 'parloit', text)
    return text

def bake_and_copy_glossary(input_tmx_path: str, output_tmx_path: str):
    ET.register_namespace('xml', 'http://w3.org')
    tree = ET.parse(input_tmx_path)
    root = tree.getroot()
    
    mutated_units = 0

    for tu in root.iter('tu'):
        en_text = None
        mia_text = None
        existing_langs = set()
        
        # Parse present items
        for tuv in tu.findall('tuv'):
            lang = tuv.attrib.get('{http://w3.org}lang', '').lower()
            existing_langs.add(lang)
            seg = tuv.find('seg')
            if seg is not None and seg.text:
                if lang == 'en':
                    en_text = seg.text.strip()
                elif lang == 'mia':
                    mia_text = seg.text.strip()

        # Only process if we have an English base and haven't appended keys yet
        if not en_text or 'fr' in existing_langs or 'fro' in existing_langs:
            continue

        try:
            # 1. Translate EN -> FR via local ltengine
            modern_fr = lt_client.translate(en_text, "en", "fr")
            
            if modern_fr:
                # 2. Convert to Old French
                old_fro = basic_fro_transformer(modern_fr)
                
                # 3. Append new language nodes into translation unit
                tuv_fr = ET.Element('tuv', {'xml:lang': 'fr'})
                ET.SubElement(tuv_fr, 'seg').text = modern_fr
                tu.append(tuv_fr)
                
                tuv_fro = ET.Element('tuv', {'xml:lang': 'fro'})
                ET.SubElement(tuv_fro, 'seg').text = old_fro
                tu.append(tuv_fro)
                
                # 4. Optional: Generate Reverse Lookup directly in the file
                # If you want explicit reverse lookup pairs, you can add them here
                
                mutated_units += 1
        except Exception as e:
            print(f"Skipping row execution for '{en_text}': {e}")

    # Write output to file
    tree.write(output_tmx_path, encoding='utf-8', xml_declaration=True)
    print(f"Baking completed. Successfully injected {mutated_units} historical multi-hop variants.")

# bake_and_copy_glossary("ilda_dictionary.tmx", "compiled_portable_dataset.tmx")
