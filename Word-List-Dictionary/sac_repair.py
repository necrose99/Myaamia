import re
from lxml import etree

def final_polish_sac(input_tmx, output_tmx):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_tmx, parser)
    root = tree.getroot()
    XML_NS = "http://www.w3.org/XML/1998/namespace"

    for tu in root.xpath('//tu'):
        try:
            en_node = tu.xpath('.//tuv[@xml:lang="en-US"]/seg')[0]
            sac_node = tu.xpath('.//tuv[@xml:lang="sac"]/seg')[0]
            
            # 1. Fix overlapping joins (e.g., 'eautifuautiful' -> 'beautiful')
            if en_node.text:
                # Deduplication logic: finds repeated chunks at the join point
                # This fixes 'eautifu' + 'autiful' overlap
                text = en_node.text
                for length in range(len(text)//2, 2, -1):
                    for i in range(len(text) - length*2 + 1):
                        chunk = text[i:i+length]
                        if text[i+length:i+length*2] == chunk:
                            text = text[:i] + text[i+length:]
                            break
                # Specific cleanup for the known Sauk PDF artifact
                en_node.text = text.replace('eautifuautiful', 'beautiful').strip()

            # 2. Split Leaked English out of Sauk tier
            if sac_node.text:
                # Looks for Sauk word followed by (it)'s or other English markers
                split_match = re.search(r'^([^\s\(]+)\s*([\(\[].*|be\s.*|it’s\s.*|to\s.*)', sac_node.text)
                if split_match:
                    sauk_part = split_match.group(1).strip()
                    leaked_eng = split_match.group(2).strip()
                    
                    sac_node.text = sauk_part
                    if en_node.text:
                        en_node.text = leaked_eng + " " + en_node.text
                    else:
                        en_node.text = leaked_eng
        except IndexError:
            continue # Skip TUs that are missing one of the language nodes

    # FIXED: Changed output_path to output_tmx
    tree.write(output_tmx, encoding="UTF-8", xml_declaration=True, pretty_print=True)
    print(f"✨ Success! {output_tmx} is ready for the master merge.")

if __name__ == "__main__":
    final_polish_sac("sac_FIXED.tmx", "sac_GOLD.tmx")