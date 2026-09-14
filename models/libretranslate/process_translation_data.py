#!/usr/bin/env python3
import os
import json
import xml.etree.ElementTree as ET
from rdflib import Graph, Namespace, RDF

def run_libretranslate_data_prep():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tmx_input = os.path.join(base_dir, "ilda_full.tmx")
    ttl_input = os.path.join(base_dir, "myaamia_lexicon.ttl")
    
    output_pairs = os.path.join(base_dir, "myaamia_pairs.txt")
    output_model_dir = os.path.join(base_dir, "model")
    output_vocab = os.path.join(output_model_dir, "vocabulary.json")
    
    os.makedirs(output_model_dir, exist_ok=True)
    unique_tokens = set()
    total_records = 0

    out = open(output_pairs, "w", encoding="utf-8")

    # 1. PARSE TMX (Extracting Myaamia, English, and IPA Tags)
    if os.path.exists(tmx_input):
        print(f"[-] Parsing TMX file with IPA tags: {tmx_input}")
        try:
            tree = ET.parse(tmx_input)
            root = tree.getroot()
            
            for tu in root.findall(".//tu"):
                ipa_val = ""
                for prop in tu.findall("prop"):
                    if prop.get("type") in ["ipa", "ipa_pronunciation", "pronunciation"]:
                        if prop.text:
                            ipa_val = prop.text.strip()

                tuv_elements = tu.findall("tuv")
                if len(tuv_elements) >= 2:
                seg1 = tuv_elements[0].find("seg")
                seg2 = tuv_elements[1].find("seg")

# Only strip if the segment text field is populated with valid string data
               lang1 = seg1.text.strip() if (seg1 is not None and seg1.text) else ""
               lang2 = seg2.text.strip() if (seg2 is not None and seg2.text) else ""

                    
                    if lang1 and lang2:
                        ipa_suffix = f"\t[{ipa_val}]" if ipa_val else ""
                        out.write(f"{lang1}\t{lang2}{ipa_suffix}\n")
                        total_records += 1
                        
                        unique_tokens.update(lang1.lower().replace("-", " ").split())
                        unique_tokens.update(lang2.lower().split())
                        if ipa_val:
                            unique_tokens.add(ipa_val)
        except Exception as e:
            print(f"[!] XML Error parsing TMX: {e}")

    # 2. PARSE TTL GRAPH (Grabbing rdfs:label directly without rigid type boundaries)
    if os.path.exists(ttl_input):
        print(f"[-] Parsing Turtle dataset file: {ttl_input}")
        g = Graph()
        g.parse(ttl_input, format="turtle")
        
        ONTOLEX = Namespace("http://w3.org")
        RDFS = Namespace("http://w3.org")
        
        # Loop through any entity possessing an active rdfs:label field
        for entry in g.subjects(RDFS.label, None):
            myaamia_word = next(g.objects(entry, RDFS.label), None)
            if not myaamia_word or str(myaamia_word).startswith("http"):
                continue
            
            myaamia_word = str(myaamia_word).strip()
            
            # Extract associated English definition comments out of the matching senses
            for sense in g.objects(entry, ONTOLEX.sense):
                for comment in g.objects(sense, RDFS.comment):
                    english_def = str(comment).strip()
                    
                    out.write(f"{myaamia_word}\t{english_def}\t[TTL]\n")
                    total_records += 1
                    
                    unique_tokens.update(myaamia_word.lower().replace("-", " ").split())
                    unique_tokens.update(english_def.lower().split())

    out.close()

    # 3. SAVE CORE VOCABULARY MATRIX
    if unique_tokens:
        vocab_list = sorted(list(unique_tokens))
        with open(output_vocab, "w", encoding="utf-8") as v_out:
            json.dump(vocab_list, v_out, indent=4, ensure_ascii=False)
        print(f"[+] Complete! Processed {total_records} rows successfully.")
        print(f"[+] Output populated: {output_pairs}")
        print(f"[+] Unique token index count: {len(vocab_list)}")
    else:
        print("[!] Warning: No data was extracted. Check your source file placements.")

if __name__ == "__main__":
    run_libretranslate_data_prep()
