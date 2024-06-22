#!/usr/bin/python3

#import translate-toolkit json
# akincikoona (num) numerals, numbers

# (c) 2011 Necrose99 ,Miami Nation ,   Others Et. Al
# This code is licensed under MIT license (see LICENSE.MD for details)
# https://github.com/necrose99/Myaamia

# Citated Sorce https://mc.miamioh.edu/ilda-myaamia/dictionary/entries/6643
# 
# https://claude.ai/ for assistance. / chatgpt  
# simular to many native American numbers,in simular
# related,likewise languages.. 
# a parallel Japanese base numbers,  1-10 repeat , 1000 , 1000 
# ie 10-1 = 11 2-10 =20 
# -aasi stem is added . 
### some TMX systems have rulesets however 
### this makes for a Quick hack to build words based on how Myammia is used. insted of forcing an SQL statment/s or AI rulesets. for now. 

   # '0': 'PLACEHOLDER_0',

###
import re
from translate.storage import tmx
import polib
import json

# Define dictionaries for the component numerals
ones = {
    '0': 'moochi',  # Placeholder for zero
    '1': 'nkoti',
    '2': 'niišwi',
    '3': 'nihswi',
    '4': 'niiwi',
    '5': 'yaalanwi',
    '6': 'kaakaathswi',
    '7': 'swaahteethswi',
    '8': 'palaani',
    '9': 'nkotimeneehki'
}

tens = {
    '2': 'niišwi mateeni',
    '3': 'nihswi mateeni',
    '4': 'niiwi mateeni',
    '5': 'yaalanwi mateeni',
    '6': 'kaakaathswi mateeni',
    '7': 'swaahteethswi mateeni',
    '8': 'palaani mateeni',
    '9': 'nkotimeneehki mateeni'
}

hundreds = {
    '1': 'nkotwaahkwe',
    '2': 'niišwaahkwe',
    '3': 'nihswaahkwe',
    '4': 'niiwaahkwe',
    '5': 'yaalanwaahkwe',
    '6': 'kaakaathswaahkwe',
    '7': 'swaahteethswaahkwe',
    '8': 'palaanwaahkwe',
    '9': 'nkotimeneehkwaahkwe'
}

thousands = {
    '1': 'mataathswaahkwe'
}

large_numbers = {
    '10000': 'PLACEHOLDER_TEN_THOUSAND',
    '1000000': 'PLACEHOLDER_MILLION',
    '1000000000': 'PLACEHOLDER_BILLION'
}

def construct_number(num_str):
    num = int(num_str)
    if num == 0:
        return ''
    elif num < 10:
        return ones[num_str[-1]]
    elif num < 20:
        return 'mataathswi ' + ones[num_str[-1]] + 'aasi'
    elif num < 100:
        return tens[num_str[-2]] + ' ' + construct_number(num_str[-1:])
    elif num < 1000:
        return hundreds[num_str[-3]] + ' ' + construct_number(num_str[-2:])
    elif num < 10000:
        if num_str[-4] == '0':
            return construct_number(num_str[-3:])
        else:
            return thousands['1'] + ' ' + construct_number(num_str[-3:])
    elif num_str in large_numbers:
        return large_numbers[num_str]
    else:
        raise ValueError(f'Number {num_str} is out of range')

def generate_tmx_entries():
    entries = []
    for num in range(1, 10001):  # Generate entries up to 10,000
        eng = str(num)
        mia = construct_number(eng)
        entries.append((eng, mia))
    return entries

def create_tmx(entries, output_file):
    tmx_data = '<tmx version="1.4"><body>'
    for eng, mia in entries:
        tmx_data += f'<tu><tuv xml:lang="en-US"><seg>{eng}</seg></tuv><tuv xml:lang="mia"><seg>{mia}</seg></tuv></tu>'
    tmx_data += '</body></tmx>'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(tmx_data)

def create_pot(entries, output_file):
    pot_file = polib.POFile()
    for eng, mia in entries:
        entry = polib.POEntry(
            msgid=eng,
            msgstr=mia,
            comment=f'Context: {eng}'
        )
        pot_file.append(entry)
    pot_file.save(output_file)


def create_json(entries, output_file, domain="messages"):
    json_data = {}
    for eng, mia in entries:
        if eng not in json_data:
            json_data[eng] = {
                "string": mia,
                "context": "",
                "comments": {
                    "reference": f"Number: {eng}"
                }
            }
    
    final_json = {
        domain: {
            "": {
                "domain": domain,
                "lang": "mia",
                "plural-forms": "nplurals=2; plural=(n != 1);"
            },
            **json_data
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_json, f, ensure_ascii=False, indent=4)

# Generate entries
entries = generate_tmx_entries()

# Create TMX file
create_tmx(entries, 'numbers.tmx')

# Create POT file
create_pot(entries, 'numbers.pot')

# Create JSON file
create_json(entries, 'numbers.json')

print("mihši neewe | misiwa newee")  # Thank you very much, big thanks

####  ### ai Dreaming ?
 ###    '1': 'mataathswaahkwe',
 ###   '10': 'mataathswi mateeni',
 ###   '100': 'mataathswi waahkwe',
###     '1000': 'mataathswi waahkwe mateeni'
###