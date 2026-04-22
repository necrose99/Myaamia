import sys
import re
import subprocess
from lxml import etree

# Regex for Scientific Latin names inside parentheses
LATIN_REGEX = re.compile(r'\(([A-Z][a-z]+ [a-z]+)\)')

def get_local_translation(text, target_lang):
    """Calls local llama.cpp build with Pascal GPU layers."""
    try:
        # Note: Adjust path if llama-cli is not in your C:\tools\llama-cpp\
        prompt = f"Translate this dictionary entry to {target_lang}: {text}"
        cmd = [
            "llama-cli", 
            "-m", "C:/models/llama-3-8b.gguf", 
            "-p", prompt, 
            "--temp", "0", "-n", "32", "-ngl", "15" # -ngl for Pascal GPU
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except Exception:
        return None

def process_ilda_tmx(input_file, output_file):
    parser = etree.XMLParser(remove_blank_text=True)
    try:
        tree = etree.parse(input_file, parser)
    except OSError:
        print(f"Error: Could not find {input_file}. Ensure the file is in the same folder.")
        return

    root = tree.getroot()
    XML_NS = "http://www.w3.org/XML/1998/namespace"
    
    # Track units for progress
    units = root.xpath('//tu')
    print(f"Processing {len(units)} entries from {input_file}...")

    for tu in units:
        # 1. Grab English segment (ILDA uses en-US)
        eng_nodes = tu.xpath('.//tuv[@xml:lang="en-US"]/seg/text()', namespaces={'xml': XML_NS})
        if not eng_nodes:
            continue
        
        eng_text = eng_nodes[0]

        # 2. Extract Latin Scientific Names (e.g., 'Canis latrans')
        # Found in entries like 'Coyote (Canis latrans)'
        latin_match = LATIN_REGEX.search(eng_text)
        if latin_match and not tu.xpath('.//tuv[@xml:lang="la"]', namespaces={'xml': XML_NS}):
            tuv_la = etree.SubElement(tu, "tuv", {f"{{{XML_NS}}}lang": "la"})
            etree.SubElement(tuv_la, "seg").text = latin_match.group(1)

        # 3. Inject Spanish & French Keys via Local LLM
        for lang_code, lang_name in [('es', 'Spanish'), ('fr', 'French')]:
            if not tu.xpath(f'.//tuv[@xml:lang="{lang_code}"]', namespaces={'xml': XML_NS}):
                translated = get_local_translation(eng_text, lang_name)
                if translated:
                    tuv_new = etree.SubElement(tu, "tuv", {f"{{{XML_NS}}}lang": lang_code})
                    etree.SubElement(tuv_new, "seg").text = translated

    tree.write(output_file, encoding="UTF-8", xml_declaration=True, pretty_print=True)
    print(f"Success! Master TMX saved to {output_file}")

if __name__ == "__main__":
    # Use the filename passed in PowerShell or default to ilda_full.tmx
    target_file = sys.argv[1] if len(sys.argv) > 1 else "ilda_full.tmx"
    process_ilda_tmx(target_file, "ALGIC_MASTER_COMBINED.tmx")