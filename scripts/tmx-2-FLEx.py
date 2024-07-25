import xml.etree.ElementTree as ET
import spacy

# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

def parse_tmx(tmx_file):
    tree = ET.parse(tmx_file)
    root = tree.getroot()
    entries = {}
    for tu in root.findall(".//tu"):
        number = tu.find(".//tuv[@xml:lang='eng_US']/seg").text
        word = tu.find(".//tuv[@xml:lang='eng_US']/seg").text
        entries[number] = word
    return entries

def create_sfm_entry(number, word):
    doc = nlp(word)
    pos = doc[0].pos_
    
    entry = f"""
\\lx {word}
\\ps {pos}
\\ge {number}
\\de Number word for {number}
\\dt {datetime.now().strftime('%d/%m/%Y')}
"""
    return entry

def create_sfm_file(entries, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for number, word in entries.items():
            sfm_entry = create_sfm_entry(number, word)
            f.write(sfm_entry)

# Main execution
tmx_file = 'numbers_eng_us.tmx'
sfm_file = 'numbers_eng_us.sfm'

entries = parse_tmx(tmx_file)
create_sfm_file(entries, sfm_file)

print(f"SFM file for FLEx has been created: {sfm_file}")