import lxml.etree as ET
import os

# Your Whitelist for the 16-Hour Grind
algic_array = [
    "mia", "sac", "kic", "sha", "pot", "oji", "otw", "ciw", 
    "alq", "ojb", "cre", "men", "unm", "del", "bla", "arp"
]

def generate_all_algic_dicts(lift_file, output_dir="dicts"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    tree = ET.parse(lift_file)
    root = tree.getroot()
    
    # Storage for found words per language
    lang_data = {lang: set() for lang in algic_array}

    # Extracting Lexemes and Cross-Language Forms
    for entry in root.xpath("//entry"):
        # Check Lexical Unit (The Primary Headword)
        for form in entry.xpath("./lexical-unit/form"):
            lang = form.get('lang')
            text = form.xpath("./text/text()")
            if lang in lang_data and text:
                lang_data[lang].add(text[0].strip().lower())
        
        # Check Allomorphs or Alternative Forms (Cognates)
        for alt in entry.xpath(".//form"):
            lang = alt.get('lang')
            text = alt.xpath("./text/text()")
            if lang in lang_data and text:
                lang_data[lang].add(text[0].strip().lower())

    # Write out each dictionary
    for lang, words in lang_data.items():
        if not words: continue
        
        sorted_words = sorted(list(words))
        dic_path = os.path.join(output_dir, f"{lang}.dic")
        aff_path = os.path.join(output_dir, f"{lang}.aff")

        with open(dic_path, 'w', encoding='utf-8') as f:
            f.write(f"{len(sorted_words)}\n")
            for word in sorted_words:
                f.write(f"{word}\n")
        
        # Create a basic UTF-8 Affix file so LibreOffice accepts it
        with open(aff_path, 'w', encoding='utf-8') as f:
            f.write("SET UTF-8\n")
            f.write("TRY esianrtolcdupmghbyfvkwzqjx\n")

    print(f"✅ Generated {len([l for l in lang_data if lang_data[l]])} Algic dictionaries in /{output_dir}")

if __name__ == "__main__":
    generate_all_algic_dicts('Myaamia_Master.lift')
