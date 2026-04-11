import os
import lxml.etree as ET
from rdflib import Graph, Namespace

# --- Configuration & Inverted Whitelist ---
# Maps Human Name to ISO for directory and file naming
ALGIC_MASTER = {
    "Blackfoot": "bft", "Arapaho": "arp", "Gros Ventre": "ats", "Cheyenne": "chy",
    "Menominee": "men", "Cree": "cre", "Swampy Cree": "csw", "Southern East Cree": "crj", 
    "Atikamekw": "atj", "Potawatomi": "pot", "Ojibwe": "oji", "Ottawa": "otw", 
    "Chippewa": "ciw", "Miami-Illinois": "mia", "Meskwaki": "sac", "Kickapoo": "kic", "Shawnee": "sha",
    "Mi'kmaq": "mic", "Western Abenaki": "abe", "Eastern Abnaki": "aaq", "Maliseet": "mal", 
    "Mohegan-Pequot": "moo", "Munsee": "mua", "Unami": "unm", 
    "Proto-Algonquian": "alg-x-proto"
}

# Reverse lookup for LIFT parsing
ISO_TO_NAME = {v: k for k, v in ALGIC_MASTER.items()}

def write_hunspell_set(output_path, name, iso, words):
    """Generates the $Language-$ISO.dic and .aff files."""
    folder_name = name.replace(" ", "_")
    target_dir = os.path.join(output_path, folder_name)
    os.makedirs(target_dir, exist_ok=True)
    
    base_filename = f"{folder_name}-{iso}"
    sorted_words = sorted(list(words))

    # Write .dic
    with open(os.path.join(target_dir, f"{base_filename}.dic"), 'w', encoding='utf-8') as f:
        f.write(f"{len(sorted_words)}\n")
        for w in sorted_words:
            f.write(f"{w}\n")

    # Write .aff
    with open(os.path.join(target_dir, f"{base_filename}.aff"), 'w', encoding='utf-8') as f:
        f.write("SET UTF-8\n")
        f.write(f"# Affix rules for {name} ({iso})\n")
        f.write(f"LANG {iso}\n")
        f.write("TRY esianrtolcdupmghbyfvkwzqjx\n")

def process_lift(lift_file, output_root):
    """Extracts words from LIFT XML structure."""
    tree = ET.parse(lift_file)
    lang_data = {iso: set() for iso in ALGIC_MASTER.values()}

    for entry in tree.xpath("//entry"):
        # Primary headwords and allomorphs
        for form in entry.xpath(".//form"):
            lang = form.get('lang')
            text = form.xpath("./text/text()")
            if lang in lang_data and text:
                lang_data[lang].add(text[0].strip().lower())

    for iso, words in lang_data.items():
        if words:
            write_hunspell_set(output_root, ISO_TO_NAME[iso], iso, words)

def process_lemon(rdf_file, output_root):
    """Extracts words from Lemon/RDF Graph using SPARQL."""
    g = Graph()
    g.parse(rdf_file, format="xml")
    ns = {"ontolex": "http://www.w3.org/ns/lemon/ontolex#"}

    for name, iso in ALGIC_MASTER.items():
        query = f"SELECT DISTINCT ?word WHERE {{ ?f ontolex:writtenRep ?word . FILTER(lang(?word) = '{iso}') }}"
        results = g.query(query, initNs=ns)
        words = {str(r.word).strip().lower() for r in results}
        
        if words:
            write_hunspell_set(output_root, name, iso, words)

def main(input_file, output_root="lexicon_build"):
    ext = os.path.splitext(input_file)[1].lower()
    print(f"🚀 Processing {input_file}...")
    
    if ext == ".lift":
        process_lift(input_file, output_root)
    elif ext in [".rdf", ".ttl", ".owl", ".xml"]:
        process_lemon(input_file, output_root)
    else:
        print("❌ Unknown file format. Use .lift or RDF (.rdf, .ttl)")
        return

    print(f"✅ Build Complete in /{output_root}")

if __name__ == "__main__":
    # Toggle between your master files here
    main('Myaamia_Master.lift') 
    # main('Algic_Ontology.rdf')
