import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

TMX_FILE = "ilda_full.tmx"
WORK_JSON = "./tmp/work.json"
LOOKAHEAD_LIMIT = 50

# Regex pattern for Latin scientific names (e.g., Acer rubrum, Canis lupus)
LATIN_PATTERN = re.compile(r'\b([A-Z][a-z]+ [a-z]+)\b')

def load_state():
    """Loads existing progress from work.json to enable script resumes."""
    if os.path.exists(WORK_JSON):
        with open(WORK_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"processed_ids": {}, "last_scanned_max": 0}

def save_state(state):
    """Persists current state to JSON."""
    os.makedirs(os.path.dirname(WORK_JSON), exist_ok=True)
    with open(WORK_JSON, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def load_tmx_ids(file_path):
    if not os.path.exists(file_path):
        return set()
    tree = ET.parse(file_path)
    ids = set()
    for elem in tree.getroot().iter():
        if elem.text:
            ids.update(int(m) for m in re.findall(r'\b\d+\b', elem.text))
    return ids

def parse_and_build_tu(entry_id, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    mya_elem = soup.select_one(".entry-headword, .headword, h1")
    eng_elem = soup.select_one(".definition, .gloss, .translation")
    
    mya_text = mya_elem.get_text(strip=True) if mya_elem else ""
    eng_text = eng_elem.get_text(strip=True) if eng_elem else ""
    
    if not mya_text or not eng_text:
        return None, None

    # Determine structural type (stem/prefix vs leaf)
    is_morpheme = mya_text.endswith('-') or mya_text.startswith('-')
    
    # Construct TMX Entry
    tu = ET.Element("tu", {"tuid": str(entry_id)})
    
    # Add morpheme property if applicable
    if is_morpheme:
        prop_type = ET.SubElement(tu, "prop", {"type": "entry_type"})
        prop_type.text = "morpheme"
    
    # Extract Latin scientific names via Regex and inject into TMX <prop>
    latin_matches = LATIN_PATTERN.findall(eng_text)
    for latin in latin_matches:
        prop_latin = ET.SubElement(tu, "prop", {"type": "scientific_name"})
        prop_latin.text = latin

    # Add Language Units
    tuv_mya = ET.SubElement(tu, "tuv", {"xml:lang": "mia"})
    ET.SubElement(tuv_mya, "seg").text = mya_text
    
    tuv_eng = ET.SubElement(tu, "tuv", {"xml:lang": "en"})
    ET.SubElement(tuv_eng, "seg").text = eng_text
    
    record = {
        "id": entry_id,
        "mia": mya_text,
        "en": eng_text,
        "is_morpheme": is_morpheme,
        "latin_names": latin_matches
    }
    
    return tu, record

# Main Process Execution
state = load_state()
existing_ids = load_tmx_ids(TMX_FILE)
max_known = max(existing_ids) if existing_ids else 0

gaps = sorted(list(set(range(1, max_known + 1)) - existing_ids))
future_candidates = list(range(max_known + 1, max_known + 1 + LOOKAHEAD_LIMIT))
candidates_to_check = [c for c in (gaps + future_candidates) if str(c) not in state["processed_ids"]]

print(f"Resuming scan... {len(candidates_to_check)} pending candidate IDs remaining.")

session = requests.Session()
headers = {"User-Agent": "Mozilla/5.0"}
new_tus = []

try:
    for entry_id in candidates_to_check:
        url = f"https://mc.miamioh.edu/dictionary/entries/{entry_id}"
        try:
            resp = session.get(url, headers=headers, timeout=10)
            if resp.status_code == 200 and "Entry Not Found" not in resp.text:
                tu_elem, data = parse_and_build_tu(entry_id, resp.text)
                if tu_elem is not None:
                    new_tus.append(tu_elem)
                    state["processed_ids"][str(entry_id)] = data
                    print(f"[FOUND] ID {entry_id}: {data['mia']} | Latin: {data['latin_names']}")
            else:
                state["processed_ids"][str(entry_id)] = {"exists": False}
        except requests.RequestException as e:
            print(f"[ERROR] ID {entry_id}: {e}")
            
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nProcess interrupted by user. Saving state before exit...")

# Save state to work.json for script resumption
save_state(state)

# Commit newly scraped XML elements directly to TMX
if new_tus and os.path.exists(TMX_FILE):
    tree = ET.parse(TMX_FILE)
    body = tree.getroot().find("body")
    if body is not None:
        for tu in new_tus:
            body.append(tu)
        tree.write(TMX_FILE, encoding="utf-8", xml_declaration=True)
        print(f"Appended {len(new_tus)} new structured entries into {TMX_FILE}")
