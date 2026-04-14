"""
repair2.py — Minimal text normalization library

Purpose:
    Fix common encoding artifacts (mojibake) from scraped or legacy text
    before further processing (TMX, XLIFF, SFM, JSON, IPA/TTS pipelines).

Features:
    - HTML entity decoding
    - UTF-8 / Latin-1 encoding repair
    - Common Windows-1252 mojibake fixes
    - Lightweight and dependency-free

Usage:
    from repair2 import clean

    text = clean(text, lang="mia")

Notes:
    - This module is intentionally minimal and safe.
    - No aggressive language transformations are performed.
    - Designed as a first-stage normalization step.
"""


# repair2.py
import re
import html

# --- COMMON MOJIBAKE FIXES (SAFE) ---
_REPAIRS = {
    "Ã«": "ë",
    "Å¡": "š",
    "Ä": "č",
    "Ã ": "à",
    "Ã¢": "â",
    "Ãª": "ê",
    "Ã®": "î",
    "Ã´": "ô",
    "Å£": "ţ",
    "Å„": "ń",
}

# Precompile regex once (fast)
_PATTERN = re.compile("|".join(map(re.escape, _REPAIRS.keys())))


# --- ENCODING FIX ---
def _fix_encoding(text: str) -> str:
    try:
        return text.encode("latin1").decode("utf-8")
    except Exception:
        return text


# --- APPLY REPAIRS ---
def _apply_repairs(text: str) -> str:
    return _PATTERN.sub(lambda m: _REPAIRS[m.group(0)], text)


# --- MAIN CLEAN FUNCTION ---
def clean(text: str, lang: str = None) -> str:
    """
    Minimal safe normalization:
    - HTML unescape
    - Fix common encoding issues
    - Apply mojibake repairs
    """

    if not text:
        return text

    # 1. HTML entities
    text = html.unescape(text)

    # 2. Encoding fix
    text = _fix_encoding(text)

    # 3. Known bad sequences
    text = _apply_repairs(text)

    return text


# --- OPTIONAL: detect still-broken text ---
def looks_broken(text: str) -> bool:
    if not text:
        return False
    return any(x in text for x in ("Ã", "Å", "Ä", "�"))

"""
TMX
Python
from repair2 import clean

seg.text = clean(seg.text, lang)

XLIFF
Python
source.text = clean(source.text, lang)

line = clean(line)

JSON / POT
Python
msgid = clean(msgid)

from repair2 import clean, looks_broken

text = clean(text)

if looks_broken(text):
    print("⚠ still suspicious:", text)
    """" 
  
