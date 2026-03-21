import xml.etree.ElementTree as ET
import time

def tmx_to_multilingual_pot(tmx_file, output_pot):
    tree = ET.parse(tmx_file)
    root = tree.getroot()
    
    with open(output_pot, 'w', encoding='utf-8') as f:
        # POT Header
        f.write('msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n')
        
        for tu in root.findall(".//tu"):
            # Get English as the msgid (key)
            eng_node = tu.find(".//tuv[@xml:lang='en-US']/seg")
            if eng_node is None: continue
            msgid = eng_node.text
            
            # Extract all available cousins
            mia = tu.find(".//tuv[@xml:lang='mia']/seg")
            pot = tu.find(".//tuv[@xml:lang='pot']/seg")
            kic = tu.find(".//tuv[@xml:lang='kic']/seg")
            oji = tu.find(".//tuv[@xml:lang='oji']/seg")
            
            # Write metadata as comments (hints for glibc/agents)
            f.write(f"#. Myaamia: {mia.text if mia is not None else 'N/A'}\n")
            f.write(f"#. Potawatomi: {pot.text if pot is not None else 'N/A'}\n")
            f.write(f"#. Kickapoo: {kic.text if kic is not None else 'N/A'}\n")
            f.write(f"#. Chippewa: {oji.text if oji is not None else 'N/A'}\n")
            
            # msgid is English, msgstr can be the Myaamia HQ translation
            f.write(f'msgid "{msgid}"\n')
            f.write(f'msgstr "{mia.text if mia is not None else ""}"\n\n')

if __name__ == "__main__":
    tmx_to_multilingual_pot("corpus/myaamia.tmx", "myaamia_cousins.pot")
