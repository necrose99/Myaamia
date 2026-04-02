import lxml.etree as ET
import spacy
from datetime import datetime

# Load SpaCy for POS tagging on English glosses
nlp = spacy.load("en_core_web_sm")

# Your "Order of Battle" for Algic Languages
algic_array = [
    "alg-x-proto", "bla", "arp", "ats", "chy", "bft",
    "men", "cre", "csw", "crj", "atj", "nsk", "moos", "crm", 
    "pot", "oji", "otw", "ciw", "alq", "ojb", "ojg", "ojs", 
    "mia", "sac", "kic", "sha", "mic", "abe", "aaq", "mal", 
    "moo", "mua", "unm", "wamp", "mas", "nrn", "qpi", "nnt", 
    "pow", "pmk", "psk", "mjy", "wiy", "yur", "en-US", "Latin", "es_mx", "fr"
]

def parse_any_tmx(tmx_file):
    ns = {'xml': 'http://www.w3.org/XML/1998/namespace'}
    tree = ET.parse(tmx_file)
    root = tree.getroot()
    entries = []

    for tu in root.xpath(".//tu"):
        # Anchor: Extract Latin from Prop if it exists
        latin_prop = tu.xpath("./prop[@type='scientific_name']/text()")
        latin = latin_prop[0] if latin_prop else "Incertae sedis"

        # Dictionary to hold found signals
        signals = {}
        for tuv in tu.xpath("./tuv"):
            lang = tuv.get(f"{{{ns['xml']}}}lang")
            seg = tuv.find("seg").text
            if lang in algic_array and seg:
                signals[lang] = seg.strip()

        if signals:
            signals['scientific_anchor'] = latin
            entries.append(signals)
            
    return entries

def create_sfm_entry(item):
    # Priority 1: Myaamia as Lexeme. Priority 2: English as Gloss.
    lex = item.get('mia') or item.get('sac') or "UNIDENTIFIED"
    gloss = item.get('en-US') or item.get('en') or "No Gloss"
    latin = item.get('scientific_anchor')

    # POS Tagging via SpaCy
    doc = nlp(gloss)
    pos = doc[0].pos_ if gloss != "No Gloss" else "N"

    # Standard Format Markers for FLEx
    entry = [f"\\lx {lex}", f"\\ps {pos}", f"\\ge {gloss}"]
    
    # Add Latin as a specific note
    if latin != "Incertae sedis":
        entry.append(f"\\nt Latin: {latin}")

    # Add other Algic cognates found in the TMX as custom markers
    for lang, text in item.items():
        if lang not in ['mia', 'en-US', 'en', 'scientific_anchor']:
            entry.append(f"\\cf {lang}: {text}") # \cf is cross-reference in FLEx

    entry.append(f"\\dt {datetime.now().strftime('%d/%m/%y')}")
    return "\n".join(entry) + "\n"

def run_conversion(input_tmx, output_sfm):
    data = parse_any_tmx(input_tmx)
    with open(output_sfm, 'w', encoding='utf-8') as f:
        for entry in data:
            f.write(create_sfm_entry(entry) + "\n")
    print(f"✅ Processed {len(data)} entries into {output_sfm}")

# Main execution loop
if __name__ == "__main__":
    # You can now point this at ANY TMX shard in your rack
    run_conversion('Mia-botanical.tmx', 'Mia-botanical.sfm')
