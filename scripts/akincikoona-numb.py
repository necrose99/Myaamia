#!/usr/bin/python3
import re
from translate.storage import tmx, po, jsonl10n
import translate-toolkit
# akincikoona (num) numerals, numbers

# https://mc.miamioh.edu/ilda-myaamia/dictionary/entries/6643
# https://claude.ai/ for assistance. 
# simular to many native American numbers,in simular
# related,likewise languages.. 
# a parallel Japanese base numbers,  1-10 repeat 
# ie 10-1 = 11 2-10 =20 
# -aasi stem is added . 


# Define dictionaries for the component numerals
ones = {
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

def construct_number(num_str):
    if int(num_str) == 0:
        return ''
    elif int(num_str) in range(1, 11):
        return ones[num_str]
    elif int(num_str) in range(11, 20):
        return 'mataathswi ' + ones[num_str[1]] + 'aasi'
    elif int(num_str) in range(20, 100):
        return tens[num_str[0]] + ' ' + construct_number(num_str[1:])
    elif int(num_str) in range(100, 1000):
        return hundreds[num_str[0]] + ' ' + construct_number(num_str[1:])
    elif int(num_str) == 1000:
        return 'mataathswaahkwe'
    else:
        raise ValueError(f'Number {num_str} is out of range')

def process_translation_file(input_file, output_file, file_type):
    if file_type == 'tmx':
        store = tmx.parsefile(input_file)
    elif file_type == 'po':
        store = po.parsefile(input_file)
    elif file_type == 'json':
        store = jsonl10n.parsefile(input_file)
    else:
        raise ValueError(f'Unsupported file type: {file_type}')

    for unit in store.units:
        source_lang = unit.source.xmllang
        target_lang = unit.target.xmllang

        if source_lang in ['eng-us', 'mia'] or target_lang == 'mia':
            source = unit.source
            numbers = re.findall(r'\d+', source)
            for num in numbers:
                myaamia_num = construct_number(num)
                if myaamia_num:
                    target = unit.target.replace(num, myaamia_num)
                    unit.target = target

    store.serialize(output_file)

# Example usage
process_translation_file('your_input_file.tmx', 'your_output_tmx_file.tmx', 'tmx')
process_translation_file('your_input_file.po', 'your_output_po_file.po', 'po')
process_translation_file('your_input_file.json', 'your_output_json_file.json', 'json')
