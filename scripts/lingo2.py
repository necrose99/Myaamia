import sqlite3
import xml.etree.ElementTree as ET
import json
from pyglossary import Glossary
from translate.storage import tmx
import polib

# SQLite connection
conn = sqlite3.connect('myaamia_linguistic_data.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY,
    myaamia_word TEXT,
    english_definition TEXT,
    part_of_speech TEXT,
    root_form TEXT,
    ipa TEXT
)
''')

def import_rail_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    for entry in root.findall('.//entry'):
        myaamia_word = entry.find('form').text
        english_def = entry.find('sense/definition[@lang="eng"]').text
        pos = entry.find('pos').text if entry.find('pos') is not None else ''
        root_form = entry.find('root').text if entry.find('root') is not None else ''
        ipa = entry.find('ipa').text if entry.find('ipa') is not None else ''
        
        cursor.execute('''
        INSERT INTO entries (myaamia_word, english_definition, part_of_speech, root_form, ipa)
        VALUES (?, ?, ?, ?, ?)
        ''', (myaamia_word, english_def, pos, root_form, ipa))
    conn.commit()

def import_flex(file_path):
    # Implement FLEX import logic here
    pass

def export_to_pyglossary(output_file):
    glos = Glossary()
    cursor.execute('SELECT myaamia_word, english_definition, part_of_speech, ipa FROM entries')
    for row in cursor.fetchall():
        entry = f"{row[1]}\nPOS: {row[2]}\nIPA: {row[3]}"
        glos.addEntry(row[0], entry)
    glos.write(output_file)

def export_for_spelling_model(dic_file, aff_file):
    cursor.execute('SELECT myaamia_word FROM entries')
    with open(dic_file, 'w', encoding='utf-8') as f:
        f.write(f"{cursor.rowcount}\n")  # Write word count
        for row in cursor.fetchall():
            f.write(f"{row[0]}\n")
    
    # Create a basic aff file
    with open(aff_file, 'w', encoding='utf-8') as f:
        f.write("SET UTF-8\n")
        f.write("TRY aeiouāēīōūčšžnmlkpthsywr'\n")
        # Add more rules as needed for Myaamia language

def export_to_tmx(output_file):
    tmx_file = tmx.tmxfile()
    cursor.execute('SELECT myaamia_word, english_definition FROM entries')
    for row in cursor.fetchall():
        tu = tmx.tmxunit(source=row[0])
        tu.target = row[1]
        tu.setsourcelang('mia')
        tu.settargetlang('eng')
        tmx_file.addunit(tu)
    tmx_file.save(output_file)

def export_to_po(output_file):
    po = polib.POFile()
    po.metadata = {
        'Project-Id-Version': '1.0',
        'Language': 'mia',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
    }
    cursor.execute('SELECT myaamia_word, english_definition FROM entries')
    for row in cursor.fetchall():
        entry = polib.POEntry(
            msgid=row[1],
            msgstr=row[0]
        )
        po.append(entry)
    po.save(output_file)

# Number processing function
def process_number_word(word):
    number_words = {
        '1': 'nkoti', '2': 'niišwi', '3': 'nihswi', '4': 'niiwi', '5': 'yaalanwi',
        '6': 'kaakaathswi', '7': 'swaahteethswi', '8': 'palaani', '9': 'nkotimeneehki', '10': 'mataathswi',
        '20': 'niišwi mateeni', '30': 'nihswi mateeni', '40': 'niiwi mateeni', '50': 'yaalanwi mateeni',
        '100': 'nkotwaahkwe', '200': 'niišwaahkwe', '1000': 'mataathswaahkwe'
    }
    
    if word.isdigit():
        num = int(word)
        if num in number_words:
            return number_words[word]
        elif num > 10 and num < 20:
            ones = num % 10
            return f"mataathswi {number_words[str(ones)]}aasi"
        elif num >= 20 and num < 100:
            tens = num // 10 * 10
            ones = num % 10
            if ones == 0:
                return number_words[str(tens)]
            else:
                return f"{number_words[str(tens)]} {number_words[str(ones)]}aasi"
        # Add more conditions for larger numbers if needed
    return word

def insert_numbers():
    numbers = [
        ('nkoti', 'One, 1', 'num'),
        ('niišwi', 'Two, 2', 'num'),
        ('nihswi', 'Three, 3', 'num'),
        ('niiwi', 'Four, 4', 'num'),
        ('yaalanwi', 'Five, 5', 'num'),
        ('kaakaathswi', 'Six, 6', 'num'),
        ('swaahteethswi', 'Seven, 7', 'num'),
        ('palaani', 'Eight, 8', 'num'),
        ('nkotimeneehki', 'Nine, 9', 'num'),
        ('mataathswi', 'Ten, 10', 'num'),
        ('mataathswi nkotaasi', 'Eleven, 11', 'num'),
        ('niišwi mateeni', 'Twenty, 20', 'num'),
        ('nkotwaahkwe', 'One hundred, 100', 'num'),
        ('mataathswaahkwe', 'One thousand, 1000', 'num')
    ]
    cursor.executemany('''
    INSERT INTO entries (myaamia_word, english_definition, part_of_speech)
    VALUES (?, ?, ?)
    ''', numbers)
    conn.commit()

if __name__ == "__main__":
    import_rail_xml("path/to/myaamia_rail.xml")
    import_flex("path/to/myaamia_flex.xml")
    insert_numbers()
    
    # Export data
    export_to_pyglossary("myaamia_glossary.dict")
    export_for_spelling_model("myaamia.dic", "myaamia.aff")
    export_to_tmx("myaamia.tmx")
    export_to_po("myaamia.po")

conn.close()