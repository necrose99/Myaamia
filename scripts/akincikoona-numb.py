#!/usr/bin/env python3

# akincikoona-numb.py
# Indexed TMX (base units) + optional expanded TMX generator

import json
import xml.sax.saxutils as saxutils

# -----------------------------
# Base lexemes (mochi / particles)
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

THOUSANDS = {
    1: "mataathswaahkwe"
}

ZERO = "moochi"

RULES = {
    "teen_prefix": "mataathswi",
    "teen_suffix": "aasi"
}

# -----------------------------
# Helpers
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

# -----------------------------
# Generator (engine builds numbers)
# -----------------------------

def construct_number(n: int) -> str:
    if n == 0:
        return ZERO

    d = decompose(n)
    parts = []

    # thousands
    if d["thousands"] > 0:
        if d["thousands"] == 1:
            parts.append(THOUSANDS[1])
        else:
            parts.append(join_parts(ONES[d["thousands"]], THOUSANDS[1]))

    # hundreds
    if d["hundreds"] > 0:
        parts.append(HUNDREDS[d["hundreds"]])

    # teens tracking (10-19)
    if d["tens"] == 1:
        if d["ones"] == 0:
            parts.append(RULES["teen_prefix"])
        else:
            comp_unit = apply_suffix(ONES[d["ones"]], RULES["teen_suffix"])
            parts.append(join_parts(RULES["teen_prefix"], comp_unit))
        return join_parts(*parts)

    # tens multipliers (20-99)
    if d["tens"] >= 2:
        parts.append(TENS[d["tens"]])

    # ones remainders (appends -aasi if attached to tens matrix)
    if d["ones"] > 0:
        if d["tens"] >= 2:
            parts.append(apply_suffix(ONES[d["ones"]], RULES["teen_suffix"]))
        else:
            parts.append(ONES[d["ones"]])

    return join_parts(*parts)

# -----------------------------
# BASE TMX (indexed units only)
# -----------------------------

def generate_base_entries():
    entries = []

    for k, v in ONES.items():
        entries.append(("ones", k, v))

    for k, v in TENS.items():
        entries.append(("tens", k, v))

    for k, v in HUNDREDS.items():
        entries.append(("hundreds", k, v))

    for k, v in THOUSANDS.items():
        entries.append(("thousands", k, v))

    # zero
    entries.append(("ones", 0, ZERO))

    return entries


def create_base_tmx(entries, output_file):
    tmx = ['<tmx version="1.4"><body>\n']

    for place, val, form in entries:
        seg = saxutils.escape(form)
        tmx.append(
            f'  <tu tuid="{place}_{val}" datatype="number">\n'
            f'    <prop type="value">{val}</prop>\n'
            f'    <prop type="place">{place}</prop>\n'
            f'    <tuv xml:lang="mia"><seg>{seg}</seg></tuv>\n'
            f'  </tu>\n'
        )

    # optional rule hints
    tmx.append(
        '  <tu tuid="rule_teen" datatype="number-rule">\n'
        f'    <prop type="pattern">10 + ones + {RULES["teen_suffix"]}</prop>\n'
        '  </tu>\n'
    )

    tmx.append('</body></tmx>')

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("".join(tmx))


# -----------------------------
# EXPANDED TMX (Completed File Matrix)
# -----------------------------

def generate_full_entries(max_n=1000):
    entries = []
    for n in range(0, max_n + 1):
        entries.append((n, construct_number(n)))
    return entries


def create_full_tmx(entries, output_file):
    """Outputs a fully completed, sequential training corpus target file."""
    tmx = ['<tmx version="1.4"><body>\n']
    
    for val, form in entries:
        seg = saxutils.escape(form)
        tmx.append(
            f'  <tu tuid="full_{val}" datatype="number">\n'
            f'    <prop type="value">{val}</prop>\n'
            f'    <tuv xml:lang="mia"><seg>{seg}</seg></tuv>\n'
            f'    <tuv xml:lang="en"><seg>{val}</seg></tuv>\n'
            f'  </tu>\n'
        )
        
    tmx.append('</body></tmx>')
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("".join(tmx))

if __name__ == "__main__":
    print("[*] Compiling core rules and executing morphophonemic checks...")
    
    # Run structural tests to certify output validity
    assert construct_number(10) == "mataathswi"
    assert construct_number(11) == "mataathswi nkotiaasi"
    assert construct_number(25) == "niišwi mateeni yaalanwaasi"
    assert construct_number(28) == "niišwi mateeni palaanaasi"
    
    base_data = generate_base_entries()
    create_base_tmx(base_data, "base_numbers.tmx")
    
    full_data = generate_full_entries(1000)
    create_full_tmx(full_data, "expanded_numbers.tmx")
    
    print("[+] TMX generator targets compiled successfully with zero syntax loopholes.")
