import re
from translate.storage import tmx
import polib
import json
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
def number_to_words(num):
    units = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    scales = ["", "thousand", "million", "billion", "trillion"]

    if num == 0:
        return "zero"

    def helper(n, scale):
        if n == 0:
            return ""
        elif n < 20:
            return units[n] + " " + scales[scale] + " "
        elif n < 100:
            return tens[n // 10] + ("-" + units[n % 10] if n % 10 != 0 else "") + " " + scales[scale] + " "
        else:
            return units[n // 100] + " hundred " + helper(n % 100, 0) + scales[scale] + " "

    result = ""
    for i in range(4, -1, -1):
        part = num // 1000**i
        if part:
            result += helper(part, i)
        num %= 1000**i

    return ' '.join(result.strip().split())

def create_entries():
    entries = {}
    # Numbers 1-100
    for i in range(1, 101):
        entries[str(i)] = number_to_words(i)
    # Hundreds
    for i in range(2, 10):
        entries[str(i*100)] = number_to_words(i*100)
    # Thousands
    for i in range(1, 101):
        entries[str(i*1000)] = number_to_words(i*1000)
    # Millions
    for i in range(1, 11):
        entries[str(i*1000000)] = number_to_words(i*1000000)
    # Billion
    entries["1000000000"] = number_to_words(1000000000)
    return entries

def create_tmx_file(entries, filename):
    tmx_file = tmx.tmxfile()
    for key, value in entries.items():
        tu = tmx.tmxunit(source=key)
        tu.target = value
        tu.srclang = 'eng_US'
        tu.targetlang = 'eng_US'
        tmx_file.addunit(tu)
    tmx_file.savefile(filename)

def create_pot_file(entries, filename):
    po = polib.POFile()
    po.metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': 'you@example.com',
        'POT-Creation-Date': '2023-07-03 12:00+0000',
        'PO-Revision-Date': '2023-07-03 12:00+0000',
        'Last-Translator': 'you <you@example.com>',
        'Language-Team': 'English <yourteam@example.com>',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
    }
    for key, value in entries.items():
        entry = polib.POEntry(
            msgid=key,
            msgstr=value,
        )
        po.append(entry)
    po.save(filename)

def create_json_file(entries, filename, lang_code="en-US"):
    json_data = {
        lang_code: {}
    }
    for key, value in entries.items():
        json_data[lang_code][key] = value
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

# Create entries
entries = create_entries()

# Create TMX file
create_tmx_file(entries, 'numbers_eng_us.tmx')

# Create POT file
create_pot_file(entries, 'numbers_eng_us.pot')

# Create JSON-i18n file
create_json_file(entries, 'numbers_eng_us.json', lang_code="en-US")

print("TMX, POT, and JSON-i18n files have been created for English (US) numbers up to one billion.")