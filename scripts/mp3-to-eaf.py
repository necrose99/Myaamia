import os
import re
import librosa
from pympi.Elan import Eaf
from lxml import etree

def brute_force_to_eaf(tmx_path, dump_dir, output_dir="eaf_output"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Load TMX Text (The Source of Truth)
    print(f"📦 Loading text from {tmx_path}...")
    parser = etree.XMLParser(recover=True)
    tree = etree.parse(tmx_path, parser)
    tmx_lookup = {}
    for tu in tree.xpath('//tu'):
        tuid = tu.get('tuid', '').replace('ilda-', '').strip()
        mia = "".join(tu.xpath('.//tuv[@xml:lang="mia"]/seg/text()'))
        en = "".join(tu.xpath('.//tuv[@xml:lang="en-US"]/seg/text()'))
        if tuid:
            tmx_lookup[tuid] = {"mia": mia, "en": en}

    # 2. Scan the Dump Folder
    print(f"🔎 Scanning crawler dump: {dump_dir}")
    audio_files = [f for f in os.listdir(dump_dir) if f.endswith('.mp3')]
    processed_count = 0
    print(f"🎧 Found {len(audio_files)} MP3s. Attempting brute-force ID match...")

    for filename in audio_files:
        # Extract the first sequence of numbers (e.g., '1234' from 'mia_1234_ver2.mp3')
        match = re.search(r'(\d+)', filename)
        if not match: continue
        
        entry_id = match.group(1)
        
        # Check if this ID exists in our TMX
        if entry_id in tmx_lookup:
            text_data = tmx_lookup[entry_id]
            abs_mp3_path = os.path.abspath(os.path.join(dump_dir, filename))
            
            try:
                # 3. Get exact duration
                duration_ms = int(librosa.get_duration(path=abs_mp3_path) * 1000)

                # 4. Create EAF with Phoneme Tier placeholder
                eaf = Eaf()
                eaf.add_linked_file(abs_mp3_path, mimetype="audio/mpeg")
                
                # Tiers: MIA, English, and a new Phoneme tier
                eaf.add_tier("Transcription-MIA")
                eaf.add_tier("Phoneme-MIA")
                eaf.add_tier("Gloss-EN")
                
                eaf.add_annotation("Transcription-MIA", 0, duration_ms, text_data['mia'])
                eaf.add_annotation("Phoneme-MIA", 0, duration_ms, "") # Placeholder for later
                eaf.add_annotation("Gloss-EN", 0, duration_ms, text_data['en'])

                # 5. Collision-proof Save
                out_name = os.path.join(output_dir, f"mia_{entry_id}.eaf")
                if os.path.exists(out_name): os.remove(out_name)
                if os.path.exists(out_name + ".bak"): os.remove(out_name + ".bak")
                
                eaf.to_file(out_name)
                processed_count += 1
                
                if processed_count % 100 == 0:
                    print(f"✅ Created {processed_count} EAFs...")

            except Exception:
                continue

    print(f"🏁 Finished! Created {processed_count} EAF files.")

if __name__ == "__main__":
    TMX_FILE = "ilda_full.tmx"
    CRAWLER_DUMP = r"C:\Users\black\GitHub\Myaamia\corpus_media\full"
    brute_force_to_eaf(TMX_FILE, CRAWLER_DUMP)