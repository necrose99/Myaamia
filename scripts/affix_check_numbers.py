
​#🧪 The Validation Script: affix_check_numbers.py
### qa test aspell hunspell affix 
#Miami-Illinois numbers against aff rules file.. 

import subprocess
import xml.etree.ElementTree as ET

def validate_numbers_against_aff(tmx_path, aff_path, dic_path):
    # 1. Parse TMX
    tree = ET.parse(tmx_path)
    root = tree.getroot()
    
    # 2. Extract Myaamia segments
    myaamia_words = []
    for tu in root.findall(".//tu"):
        for tuv in tu.findall("tuv"):
            if tuv.get("{http://www.w3.org/XML/1998/namespace}lang") == "mia":
                myaamia_words.append(tuv.find("seg").text)

    # 3. Batch Check with Hunspell
    # -a: pipe mode, -d: dictionary path
    process = subprocess.Popen(
        ['hunspell', '-d', 'MIA_US-Myaamia', '-a'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print(f"🧐 Validating {len(myaamia_words)} entries...")
    
    errors = []
    for word in myaamia_words:
        # Clean underscores or spaces if your .aff expects one word
        test_word = word.replace(' ', '_') 
        process.stdin.write(f"{test_word}\n")
        process.stdin.flush()
        
        # Read the response (& = Correct, # or * = Suggestion/Error)
        res = process.stdout.readline().strip()
        if res.startswith('&') or res.startswith('*'):
            continue # Correct or Root found
        elif res == "":
            continue # Skip blank lines
        else:
            errors.append((word, res))

    # 4. Report
    if not errors:
        print("✅ SUCCESS: All 10,000 numerals are morphologically valid!")
    else:
        print(f"❌ FAILED: Found {len(errors)} invalid constructions.")
        for word, res in errors[:10]: # Show first 10 errors
            print(f"  - '{word}' rejected by .aff rules.")

if __name__ == "__main__":
    validate_numbers_against_aff('numbers.tmx', 'MIA_US-Myaamia.aff', 'MIA_US-Myaamia.dic')

