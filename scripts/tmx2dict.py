import xml.etree.ElementTree as ET

def tmx_to_hunspell(tmx_input, dic_output, lang_code='mia'):
    tree = ET.parse(tmx_input)
    root = tree.getroot()
    
    entries = []
    
    for tu in root.findall(".//tu"):
        eng_text = ""
        mia_text = ""
        flags = ""
        
        # 1. Extract English (Comment) and Myaamia (Word)
        for tuv in tu.findall("tuv"):
            lang = tuv.get("{http://www.w3.org/XML/1998/namespace}lang")
            seg = tuv.find("seg").text
            if lang == "en-US":
                eng_text = seg
            elif lang == lang_code:
                mia_text = seg
        
        # 2. Predictive Flagging (The "Linguistic Logic")
        # Example: If it's a number, give it the 'N' flag
        if any(char.isdigit() for char in eng_text):
            flags = "/N"
        # Example: If it ends in 'a' or 'wa', it's likely an Animate Noun
        elif mia_text.endswith(('a', 'wa')):
            flags = "/AN" 

        if mia_text:
            entries.append(f"{mia_text}{flags} #{eng_text}")

    # 3. Write .dic file with Hunspell Header
    with open(dic_output, 'w', encoding='utf-8') as f:
        f.write(f"{len(entries)}\n")
        for entry in entries:
            f.write(f"{entry}\n")

    print(f"✅ Created {dic_output} with {len(entries)} commented entries.")

if __name__ == "__main__":
    tmx_to_hunspell('Algic.tmx', 'MIA_US-Myaamia.dic')



import xml.etree.ElementTree as ET
import datetime

def tmx_to_hunspell_dict(tmx_input, dic_output, target_lang='mia'):
    try:
        tree = ET.parse(tmx_input)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing TMX: {e}")
        return

    entries = []
    
    # Namespace handling for xml:lang
    ns = {'xml': 'http://www.w3.org/XML/1998/namespace'}

    for tu in root.findall(".//tu"):
        eng_text = ""
        target_text = ""
        context_note = ""
        
        # 1. Extract Context Note (Sociolinguistic Metadata)
        note_el = tu.find("note")
        if note_el is not None:
            context_note = note_el.text.strip()

        # 2. Extract Segments
        for tuv in tu.findall("tuv"):
            lang = tuv.get(f"{{{ns['xml']}}}lang")
            seg_el = tuv.find("seg")
            if seg_el is None or seg_el.text is None:
                continue
                
            if lang == "en-US":
                eng_text = seg_el.text.strip()
            elif lang == target_lang:
                target_text = seg_el.text.strip()

        if not target_text:
            continue

        # 3. Apply Flag Logic (Predictive Analytics)
        flags = ""
        # Rule: If it's a number (akincikoona), apply the /N flag
        if "num" in context_note.lower() or any(char.isdigit() for char in eng_text):
            flags = "/N"
        
        # 4. Construct Comment with Register Info
        comment = eng_text
        if "women" in context_note.lower() or "feminine" in context_note.lower():
            comment += " [FEMININE REGISTER]"
        elif "affirm" in context_note.lower():
            comment += " [AFFIRMATIVE]"

        entries.append(f"{target_text}{flags} #{comment}")

    # 5. Write .dic with Hunspell Count Header
    with open(dic_output, 'w', encoding='utf-8') as f:
        f.write(f"{len(entries)}\n")
        for entry in entries:
            f.write(f"{entry}\n")

    print(f"🚀 Created {dic_output} with {len(entries)} entries at {datetime.datetime.now()}")

if __name__ == "__main__":
    # Point this to your Algic.tmx
    tmx_to_hunspell_dict('Algic.tmx', 'MIA_US-Myaamia.dic')
def get_comment_with_meta(tu):
    eng = tu.find("tuv[@xml:lang='en-US']/seg").text
    note = tu.find("note").text if tu.find("note") is not None else ""
    
    if "women" in note.lower():
        return f"#{eng} [FEMININE REGISTER]"
    return f"#{eng}"
  def get_hunspell_flag(mia_word, pos_tag):
    if pos_tag == "PART":
        return ""  # No flags for particles like iihia
    elif mia_word.endswith("aki"):
        return "/PL" # Plural flag
    return ""

