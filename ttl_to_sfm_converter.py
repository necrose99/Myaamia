#!/usr/bin/env python3
"""
Myaamia-Illinois Ontology Pipeline: Turtle (TTL) to SIL Standard Format Marker (.sfm)
Flattens linked semantic entries down to linear lexicographical record markers.
"""
import re
import sys

def parse_ttl_to_sfm(input_ttl_path, output_sfm_path):
    print(f"[*] Reading Turtle semantic model from: {input_ttl_path}")
    with open(input_ttl_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split the raw string into isolated block resource nodes (delimited by spaces and periods)
    # This captures the entry anchors (e.g., ex:ilda_13) and their trailing property arrays
    raw_nodes = re.split(r'\n+(?=ex:ilda_\d+\b)', content)
    
    sfm_records = []
    processed_count = 0

    for node in raw_nodes:
        if not node.strip() or 'ontolex:LexicalEntry' not in node:
            continue
            
        # 1. Isolate the core system identifier integer matching your project schema
        id_match = re.search(r'ex:ilda_(\d+)\b', node)
        if not id_match:
            continue
        entry_id = id_match.group(1)

        # 2. Extract out the primary entry headword (Lexeme String)
        lexeme_match = re.search(r'rdfs:label\s+"([^"]+)"@mia', node)
        lexeme = lexeme_match.group(1) if lexeme_match else ""
        if not lexeme:
            continue

        # 3. Handle explicit parts of speech strings or default down unresolved matrices
        pos_match = re.search(r'lexinfo:partOfSpeech\s+lexinfo:(\w+)', node)
        if pos_match:
            pos = pos_match.group(1)
        elif 'alg:posUnresolved true' in node:
            pos = "Unresolved/Particle Matrix"
        else:
            pos = "Particle/Unclassified"

        # 4. Search further down the node configuration to locate the attached rdfs:comment Sense string
        # This scans across multi-line triple definitions to gather the contextual translation gloss
        sense_pattern = rf'ex:ilda_{entry_id}_sense\b.*?rdfs:comment\s+"([^"]+)"@en'
        sense_match = re.search(sense_pattern, content, re.DOTALL)
        gloss = sense_match.group(1) if sense_match else "No English gloss indexed"

        # 5. Compile variables dynamically into the linear backslash layout
        sfm_block = []
        sfm_block.append(f"\\lx {lexeme}")
        sfm_block.append(f"\\ps {pos}")
        sfm_block.append(f"\\ge {gloss}")
        sfm_block.append(f"\\id {entry_id}")
        
        # Append compiled string block
        sfm_records.append("\n".join(sfm_block))
        processed_count += 1

    # Write out compiled entries cleanly to disk target
    with open(output_sfm_path, 'w', encoding='utf-8') as out_f:
        out_f.write("\n\n".join(sfm_records) + "\n")
        
    print(f"[+] SFM conversion successful. {processed_count} data entries mapped cleanly.")

if __name__ == "__main__":
    # Fallback default file declarations matching your structural layout
    input_file = "mia_ilda_lexicon.ttl"
    output_file = "mia_ilda_lexicon.sfm"
    
    if len(sys.argv) > 2:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        
    parse_ttl_to_sfm(input_file, output_file)
