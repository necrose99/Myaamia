import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from xml.dom import minidom

TMX_FILE = "ilda_full.tmx"
WORK_JSON = "./tmp/work.json"
AUDIO_JSON = "./audio.json"
LOOKAHEAD_LIMIT = 50000

# Regex pattern for Latin scientific names (e.g., Acer rubrum, Canis lupus)
LATIN_PATTERN = re.compile(r'\b([A-Z][a-z]+ [a-z]+)\b')

def load_state():
    """Loads existing progress from work.json to enable script resumes."""
    if os.path.exists(WORK_JSON):
        with open(WORK_JSON, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("[WARNING] work.json corrupted. Initializing fresh runtime layout state.")
    return {"processed_ids": {}, "last_scanned_max": 0}

def save_state(state):
    """Persists current state to JSON."""
    os.makedirs(os.path.dirname(WORK_JSON), exist_ok=True)
    with open(WORK_JSON, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def load_audio_manifest():
    """Loads the audio lookup file structure to log target mp3 tracks."""
    if os.path.exists(AUDIO_JSON):
        with open(AUDIO_JSON, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass
    return {}

def save_audio_manifest(manifest):
    """Saves updated vocabulary string keys and audio maps."""
    with open(AUDIO_JSON, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

def load_tmx_ids(file_path):
    """Parses structural TMX file to discover existing numeric database markers."""
    if not os.path.exists(file_path):
        return set()
    try:
        tree = ET.parse(file_path)
        ids = set()
        for tu in tree.getroot().findall(".//tu"):
            tuid = tu.get("tuid")
            if tuid and tuid.isdigit():
                ids.add(int(tuid))
        return ids
    except Exception as e:
        print(f"[ERROR] Failed to extract IDs from legacy TMX layout file: {e}")
        return set()

def parse_and_build_tu(entry_id, html_content, audio_manifest):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Primary Stem & Gloss Mapping
    mya_elem = soup.select_one(".entry-headword, .headword, h1, h2, h3, h4")
    eng_elem = soup.select_one(".definition, .gloss, .translation, .entry-definition")
    
    if not mya_elem or not eng_elem:
        return None, None

    mya_text = mya_elem.get_text(strip=True)
    eng_text = eng_elem.get_text(strip=True)
    
    if not mya_text or "ilda dictionary" in mya_text.lower():
        return None, None
        
    is_morpheme = mya_text.endswith('-') or mya_text.startswith('-')

    tu = ET.Element("tu", {"tuid": str(entry_id)})
    
    # Metadata Properties Array Definition
    if is_morpheme:
        ET.SubElement(tu, "prop", {"type": "entry_type"}).text = "morpheme"
        
    url_prop = ET.SubElement(tu, "prop", {"type": "url"})
    url_prop.text = f"https://miamioh.edu{entry_id}"

    # Base Headword Variant Declarations
    tuv_mya = ET.SubElement(tu, "tuv", {"xml:lang": "mia"})
    ET.SubElement(tuv_mya, "seg").text = mya_text
    
    tuv_eng = ET.SubElement(tu, "tuv", {"xml:lang": "en"})
    ET.SubElement(tuv_eng, "seg").text = eng_text

    # --- MINOR IMPROVEMENT: NATIVE LATIN TAXONOMY VARIANT PROCESSING ---
    latin_matches = list(set(LATIN_PATTERN.findall(eng_text)))
    for latin in latin_matches:
        # Append as full translation variants for parallel alignment pipelines
        tuv_lat = ET.SubElement(tu, "tuv", {"xml:lang": "la"})
        ET.SubElement(tuv_lat, "seg").text = latin
        
        # Keep property attribute tag for legacy backwards compatibility
        ET.SubElement(tu, "prop", {"type": "scientific_name"}).text = latin

    # 2. Extract Embedded Audio Payload Links (Bypasses missing card flaw)
    # Target all anchor endpoints matching vocabulary audio registers
    for audio_link in soup.find_all("a", href=re.compile(r"\.mp3", re.IGNORECASE)):
        mp3_url = audio_link.get("href", "").strip()
        if mp3_url:
            # Clean up the localized anchor label or map context definitions
            label_text = audio_link.get_text(strip=True)
            if not label_text:
                label_text = audio_link.parent.get_text(strip=True)
            label_text = re.sub(r"\s+", " ", label_text).split("http")[0].strip()
            
            # Use specific Myaamia phrase token as structural index register key
            target_key = label_text if label_text else mya_text
            if target_key not in audio_manifest:
                audio_manifest[target_key] = []
            if mp3_url not in audio_manifest[target_key]:
                audio_manifest[target_key].append(mp3_url)

    # 3. Extract Child Segments (Inflections, Commands, Sentences)
    child_segments = []
    for row in soup.select("table tr, .paradigm-row, .sentence-row, .entry-table tr"):
        cols = row.find_all(["td", "th"])
        if len(cols) >= 2:
            mya_child = cols[0].get_text(strip=True)
            eng_child = cols[1].get_text(strip=True)
            
            if mya_child and eng_child and mya_child.lower() != "myaamia" and eng_child.lower() != "english":
                parent_section = row.find_parent(["div", "section"])
                section_name = "child_segment"
                if parent_section:
                    header = parent_section.find(["h2", "h3", "h4", "h5", "span"])
                    if header:
                        section_name = header.get_text(strip=True).lower().replace(" ", "_")

                # Structural Multi-Property Node Insertion
                child_prop = ET.SubElement(tu, "prop", {"type": section_name})
                child_prop.text = f"{mya_child} ||| {eng_child}"
                
                child_segments.append({
                    "category": section_name,
                    "mia": mya_child,
                    "en": eng_child
                })

    record = {
        "id": entry_id,
        "mia": mya_text,
        "en": eng_text,
        "is_morpheme": is_morpheme,
        "latin_names": latin_matches,
        "child_segments": child_segments
    }
    
    return tu, record

def initialize_empty_tmx(file_path):
    """Constructs a basic valid template skeleton if your target file structure doesn't exist."""
    root = ET.Element("tmx", version="1.4")
    header = ET.SubElement(root, "header", {
        "creationtool": "ILDA_Scraper_Compiler",
        "segtype": "phrase",
        "o-tmf": "UTF-8",
        "adminlang": "en-US",
        "srclang": "mia",
        "datatype": "plaintext"
    })
    ET.SubElement(root, "body")
    raw_str = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(raw_str)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(reparsed.toprettyxml(indent="  "))

# --- Execution Flow ---
if __name__ == "__main__":
    state = load_state()
    audio_manifest = load_audio_manifest()
    
    if not os.path.exists(TMX_FILE):
        initialize_empty_tmx(TMX_FILE)
        
    existing_ids = load_tmx_ids(TMX_FILE)
    max_known = max(existing_ids) if existing_ids else 0

    gaps = sorted(list(set(range(1, max_known + 1)) - existing_ids))
    future_candidates = list(range(max_known + 1, max_known + 1 + LOOKAHEAD_LIMIT))
    candidates_to_check = [c for c in (gaps + future_candidates) if str(c) not in state["processed_ids"]]

    print(f"Resuming scan... {len(candidates_to_check)} pending candidate IDs remaining.")

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    new_tus = []

    try:
        for index, entry_id in enumerate(candidates_to_check):
            # Fixed absolute root routing location path map configuration
            url = f"https://miamioh.edu{entry_id}"
            try:
                resp = session.get(url, headers=headers, timeout=15)
                
                if resp.status_code == 200 and "Entry Not Found" not in resp.text and "headword" in resp.text.lower():
                    tu_elem, data = parse_and_build_tu(entry_id, resp.text, audio_manifest)
                    if tu_elem is not None:
                        new_tus.append(tu_elem)
                        state["processed_ids"][str(entry_id)] = data
                        print(f"[FOUND] ID {entry_id}: {data['mia']} | Latin Variants: {data['latin_names']}")
                    else:
                        state["processed_ids"][str(entry_id)] = {"exists": False}
                else:
                    state["processed_ids"][str(entry_id)] = {"exists": False}
                    
            except requests.RequestException as e:
                print(f"[ERROR Network Fault] ID {entry_id}: {e}")
                
            # Intermittent memory flushes to prevent local workspace parameter data losses
            if index % 25 == 0 and index > 0:
                save_state(state)
                save_audio_manifest(audio_manifest)
                
            time.sleep(0.15)
            
    except KeyboardInterrupt:
        print("\nProcess execution loop paused via manual escape. Writing file arrays out to disk...")

    save_state(state)
    save_audio_manifest(audio_manifest)

    # Clean multi-line indentation write loop back into master TMX file
    if new_tus:
        try:
            tree = ET.parse(TMX_FILE)
            body = tree.getroot().find("body")
            if body is not None:
                for tu in new_tus:
                    body.append(tu)
                
