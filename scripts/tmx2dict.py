import xml.etree.ElementTree as ET
from pathlib import Path

# The 'Rack' Configuration
ALGIC_ARRAY = [
    "alg-x-proto", "bla", "arp", "ats", "chy", "bft", "men", "cre", "csw", 
    "crj", "atj", "nsk", "moos", "crm", "pot", "oji", "otw", "ciw", "alq", 
    "ojb", "ojg", "ojs", "mia", "sac", "kic_us", "kic_mx", "sha", "mic", 
    "abe", "aaq", "mal", "moo", "mua", "unm", "wamp", "mas", "nrn", "qpi", 
    "nnt", "pow", "pmk", "psk", "mjy", "wiy", "yur"
]

# Output Directory
EXPORT_BASE = Path("./Myaamia/Aspell-Hunspell")
TMX_SOURCE = Path("./data_shards/tmx")

def create_affix_shell(lang_code, path):
    """Writes a basic .aff shell if it doesn't exist."""
    aff_content = f"SET UTF-8\nTITLE {lang_code.upper()} Affix Rules\n\nREP 4\nREP š sh\nREP ž zh\nREP č ch\nREP ʼ '\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(aff_content)

def unified_algic_dump():
    """Iterates through the rack, deduplicates, sorts, and bakes."""
    EXPORT_BASE.mkdir(parents=True, exist_ok=True)

    for lang in ALGIC_ARRAY:
        tmx_file = TMX_SOURCE / f"Algic-{lang}.tmx"
        if not tmx_file.exists():
            continue

        print(f"🛰️  Processing: {lang}")
        
        entries = set() # Use a set for automatic deduplication
        ns = {'xml': 'http://www.w3.org/XML/1998/namespace'}

        try:
            tree = ET.parse(tmx_file)
            root = tree.getroot()
            
            for tu in root.findall(".//tu"):
                # Extract English and Target
                eng = tu.find(f".//tuv[@{{{ns['xml']}}}lang='en-US']/seg")
                target = tu.find(f".//tuv[@{{{ns['xml']}}}lang='{lang}']/seg")
                note = tu.find("note")
                
                if target is not None and target.text:
                    word = target.text.strip()
                    trans = eng.text.strip() if eng is not None else "undocumented"
                    comment = f"#{trans}"
                    
                    # Optional: Add metadata from notes to the comment
                    if note is not None and note.text:
                        comment += f" [{note.text.strip()}]"
                    
                    entries.add(f"{word} {comment}")

            # --- DUMP DICTIONARY ---
            sorted_entries = sorted(list(entries)) # Alphabetical dump
            dic_path = EXPORT_BASE / f"{lang}.dic"
            with open(dic_path, "w", encoding="utf-8") as f:
                f.write(f"{len(sorted_entries)}\n")
                for e in sorted_entries:
                    f.write(f"{e}\n")

            # --- DUMP AFFIX SHELL ---
            aff_path = EXPORT_BASE / f"{lang}.aff"
            if not aff_path.exists():
                create_affix_shell(lang, aff_path)

            print(f"✅ Baked {lang}: {len(sorted_entries)} entries.")

        except Exception as e:
            print(f"❌ Error in {lang} seam: {e}")

if __name__ == "__main__":
    unified_algic_dump()