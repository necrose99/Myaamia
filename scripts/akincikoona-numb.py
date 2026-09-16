#!/usr/bin/env python3
# akincikoona-numb.py - Refactored for Archival Variant Integration (v1.1 Run)

import json
import xml.sax.saxutils as saxutils

# -----------------------------
# Core Lexemes & Archival Additions
# -----------------------------

ONES = {
    1: "nkoti",
    2: "niišwi",
    3: "nihswi",
    4: "niiwi",
    5: "yaalanwi",
    6: "kaakaathswi",
    7: "swaahteethswi",
    8: "palaani",
    9: "nkotimeneehki"
}

TENS = {
    2: "niišwi mateeni",
    3: "nihswi mateeni",
    4: "niiwi mateeni",
    5: "yaalanwi mateeni",
    6: "kaakaathswi mateeni",
    7: "swaahteethswi mateeni",
    8: "palaani mateeni",
    9: "nkotimeneehki mateeni"
}

HUNDREDS = {
    1: "nkotwaahkwe",
    2: "niišwaahkwe",
    3: "nihswaahkwe",
    4: "niiwaahkwe",
    5: "yaalanwaahkwe",
    6: "kaakaathswaahkwe",
    7: "swaahteethswaahkwe",
    8: "palaanwaahkwe",
    9: "nkotimeneehkwaahkwe"
}

# Unified Modern and Archival Thousands/Ten-Thousands Matrix
THOUSANDS = {
    1: "mataathswaahkwe",  # Modern reconstruction base
    1000: "mittahsoak",    # Archival entry (1,000 / mille)
    10000: "kiciouae"     # Archival entry (10,000 / dix mille)
}

RULES = {
    "teen_prefix": "mataathswi",
    "teen_suffix": "aasi"
}

# -----------------------------
# Morphological Engine
# -----------------------------

def join_parts(*parts):
    return " ".join(p for p in parts if p)

def decompose(n):
    return {
        "thousands": n // 1000,
        "hundreds": (n % 1000) // 100,
        "tens": (n % 100) // 10,
        "ones": n % 10
    }

def apply_suffix(base_word: str, suffix: str) -> str:
    """Handles morphophonemic structural sandhi vowel dropping."""
    if base_word.endswith("wi"):
        return base_word[:-2] + "waasi" if suffix == "aasi" else base_word[:-2] + suffix
    elif base_word.endswith("i"):
        return base_word[:-1] + suffix
    return base_word + suffix

def construct_number(n: int) -> str:
    # Explicit omission of a literal mathematical zero place holder 
    if n <= 0:
        return ""

    # Direct archival overrides for precise historical milestone constants
    if n == 1000:
        return THOUSANDS[1000]
    if n == 10000:
        return THOUSANDS[10000]

    d = decompose(n)
    parts = []

    # Thousands logic scale
    if d["thousands"] > 0:
        if d["thousands"] == 1:
            parts.append(THOUSANDS[1])
        else:
            parts.append(join_parts(ONES[d["thousands"]], THOUSANDS[1]))

    # Hundreds scale
    if d["hundreds"] > 0:
        parts.append(HUNDREDS[d["hundreds"]])

    # Teens tracking (10-19)
    if d["tens"] == 1:
        if d["ones"] == 0:
            parts.append(RULES["teen_prefix"])
        else:
            comp_unit = apply_suffix(ONES[d["ones"]], RULES["teen_suffix"])
            parts.append(join_parts(RULES["teen_prefix"], comp_unit))
        return join_parts(*parts)

    # Tens multipliers (20-99)
    if d["tens"] >= 2:
        parts.append(TENS[d["tens"]])

    # Ones remainders with conditional morphophonemic suffix attachment
    if d["ones"] > 0:
        if d["tens"] >= 2:
            parts.append(apply_suffix(ONES[d["ones"]], RULES["teen_suffix"]))
        else:
            parts.append(ONES[d["ones"]])

    return join_parts(*parts)

# -----------------------------
# Compilation Outputs (TMX Generators)
# -----------------------------

def generate_full_entries(max_n=10000):
    entries = []
    for n in range(1, max_n + 1):
        num_str = construct_number(n)
        if num_str: # Avoid empty zero elements
            entries.append((n, num_str))
    return entries

def create_full_tmx(entries, output_file=r"C:\tools\data\expanded_numbers.tmx"):
    """Generates an unindexed, raw TMX parallel text array inside tools scratchspace."""
    tmx = ['<tmx version="1.4"><body>\n']
    
    for val, form in entries:
        seg = saxutils.escape(form)
        tmx.append(
            f'  <tu tuid="num_{val}" datatype="numerical-matrix">\n'
            f'    <prop type="int_value">{val}</prop>\n'
            f'    <tuv xml:lang="mia"><seg>{seg}</seg></tuv>\n'
            f'    <tuv xml:lang="en"><seg>{val}</seg></tuv>\n'
            f'  </tu>\n'
        )
        
    tmx.append('</body></tmx>')
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("".join(tmx))

if __name__ == "__main__":
    print("[*] Running archival verification and Sandhi text validation...")
    
    # Assert checks verify that morphophonemic sandhi rules parse flawlessly
    assert construct_number(10) == "mataathswi"
    assert construct_number(11) == "mataathswi nkotaasi"
    assert construct_number(25) == "niišwi mateeni yaalanwaasi"
    assert construct_number(1000) == "mittahsoak"
    assert construct_number(10000) == "kiciouae"
    
    print("[+] Structural validation successful. Generating training corpus grid...")
    full_dataset = generate_full_entries(10000)
    create_full_tmx(full_dataset)
    print(f"[+] Complete parallel matrix baked! Output isolated from Git tracking.")
