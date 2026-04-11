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

    # teens
    if d["tens"] == 1:
        if d["ones"] == 0:
            parts.append(RULES["teen_prefix"])
        else:
            parts.append(join_parts(
                RULES["teen_prefix"],
                ONES[d["ones"]] + RULES["teen_suffix"]
            ))
        return join_parts(*parts)

    # tens
    if d["tens"] >= 2:
        parts.append(TENS[d["tens"]])

    # ones
    if d["ones"] > 0:
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
    tmx = ['<tmx version="1.4"><body>']

    for place, val, form in entries:
        seg = saxutils.escape(form)

        tmx.append(
            f'<tu tuid="{place}_{val}" datatype="number">'
            f'<prop type="value">{val}</prop>'
            f'<prop type="place">{place}</prop>'
            f'<tuv xml:lang="mia"><seg>{seg}</seg></tuv>'
            f'</tu>'
        )

    # optional rule hints
    tmx.append(
        '<tu tuid="rule_teen" datatype="number-rule">'
        f'<prop type="pattern">10 + ones + {RULES["teen_suffix"]}</prop>'
        '</tu>'
    )

    tmx.append('</body></tmx>')

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("".join(tmx))


# -----------------------------
# EXPANDED TMX (optional)
# -----------------------------

def generate_full_entries(max_n=1000):
    entries = []
    for n in range(0, max_n + 1):
        entries.append((n, construct_number(n)))
    return entries


def create_full_tmx(entries, output_file):
    tmx
