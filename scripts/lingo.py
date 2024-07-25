import sqlite3
import xml.etree.ElementTree as ET
import json
import os
from pyglossary import Glossary
from pywebcopy import save_website
import speech_recognition as sr
from pydub import AudioSegment

# SQLite connection
conn = sqlite3.connect('myaamia_linguistic_data.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY,
    myaamia_word TEXT,
    english_us_definition TEXT,
    french_definition TEXT,
    ipa TEXT,
    audio_file TEXT,
    source TEXT,
    sauk_fox_kickapoo TEXT,
    ojibwe_potawatomi_ottawa TEXT
)
''')

# Myaamia phoneme to IPA mapping
myaamia_to_ipa = {
    'p': 'p', 't': 't', 'č': 'tʃ', 'k': 'k', ''': 'ʔ',
    's': 's', 'š': 'ʃ', 'h': 'h',
    'm': 'm', 'n': 'n',
    'w': 'w', 'l': 'l', 'y': 'j',
    'a': 'a', 'e': 'e', 'i': 'i', 'o': 'o'
}

def myaamia_to_ipa_convert(text):
    return ''.join(myaamia_to_ipa.get(char, char) for char in text)

def scrape_website(url, project_folder):
    kwargs = {'project_name': 'myaamia_language', 'bypass_robots': True, 'debug': True}
    save_website(
        url=url,
        project_folder=project_folder,
        **kwargs
    )

def process_downloaded_content(project_folder):
    for root, dirs, files in os.walk(project_folder):
        for file in files:
            if file.endswith('.mp3'):
                audio_file = os.path.join(root, file)
                myaamia_word = os.path.splitext(file)[0]
                ipa = myaamia_to_ipa_convert(myaamia_word)  # Convert filename to IPA
                
                cursor.execute('''
                INSERT INTO entries (myaamia_word, audio_file, ipa, source)
                VALUES (?, ?, ?, ?)
                ''', (myaamia_word, audio_file, ipa, 'website'))
    conn.commit()

def import_flex(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    for entry in root.findall('.//entry'):
        myaamia_word = entry.find('lexeme/form').text
        english_def = entry.find('sense/gloss[@lang="eng"]').text
        ipa = myaamia_to_ipa_convert(myaamia_word)
        cursor.execute('''
        INSERT INTO entries (myaamia_word, english_us_definition, ipa, source)
        VALUES (?, ?, ?, ?)
        ''', (myaamia_word, english_def, ipa, 'FLEX'))
    conn.commit()

def export_to_pyglossary(output_file):
    glos = Glossary()
    cursor.execute('SELECT myaamia_word, english_us_definition, french_definition, ipa, audio_file, sauk_fox_kickapoo, ojibwe_potawatomi_ottawa FROM entries')
    for row in cursor.fetchall():
        entry = f"English (US): {row[1] or 'N/A'}\nFrench: {row[2] or 'N/A'}\nIPA: {row[3] or 'N/A'}\nAudio: {row[4] or 'N/A'}\nSauk-Fox-Kickapoo: {row[5] or 'N/A'}\nOjibwe-Potawatomi-Ottawa: {row[6] or 'N/A'}"
        glos.addEntry(row[0], entry)
    glos.write(output_file)

def export_for_ai_model(output_file):
    cursor.execute('SELECT myaamia_word, english_us_definition, french_definition, ipa, audio_file, sauk_fox_kickapoo, ojibwe_potawatomi_ottawa FROM entries')
    data = [{
        "myaamia": row[0],
        "english_us": row[1],
        "french": row[2],
        "ipa": row[3],
        "audio": row[4],
        "sauk_fox_kickapoo": row[5],
        "ojibwe_potawatomi_ottawa": row[6]
    } for row in cursor.fetchall()]
    with open(output_file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def export_for_spelling_model(output_file, aff_file):
    cursor.execute('SELECT myaamia_word FROM entries')
    with open(output_file, 'w', encoding='utf-8') as f:
        for row in cursor.fetchall():
            f.write(f"{row[0]}\n")
    
    # Create a basic aff file
    with open(aff_file, 'w', encoding='utf-8') as f:
        f.write("SET UTF-8\n")
        f.write("TRY ptkčʔsšhmnwlyaeio'\n")  # Based on Myaamia phonology
        f.write("LANG myaamia\n")
        # Add more rules as needed for Myaamia language

if __name__ == "__main__":
    # Scrape website
    scrape_website("https://mc.miamioh.edu/ilda-myaamia/dictionary", "./myaamia_website_data")
    
    # Process downloaded content
    process_downloaded_content("./myaamia_website_data")
    
    # Import Flex data
    import_flex("path/to/myaamia_flex.xml")
    
    # Export data
    export_to_pyglossary("myaamia_glossary.dict")
    export_for_ai_model("myaamia_dataset.json")
    export_for_spelling_model("myaamia.dic", "myaamia.aff")

conn.close()