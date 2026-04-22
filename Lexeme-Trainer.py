#!/usr/bin/env python3
import pandas as pd
from rapidfuzz import process

# --- Your Lexeme Dictionaries ---
ONES = {1: "nkoti", 2: "niišwi", 3: "nihswi", 4: "niiwi", 5: "yaalanwi", 6: "kaakaathswi", 7: "swaahteethswi", 8: "palaani", 9: "nkotimeneehki"}
TENS = {2: "niišwi mateeni", 3: "nihswi mateeni", 4: "niiwi mateeni", 5: "yaalanwi mateeni", 6: "kaakaathswi mateeni", 7: "swaahteethswi mateeni", 8: "palaani mateeni", 9: "nkotimeneehki mateeni"}
HUNDREDS = {1: "nkotwaahkwe", 2: "niišwaahkwe", 3: "nihswaahkwe", 4: "niiwaahkwe", 5: "yaalanwaahkwe", 6: "kaakaathswaahkwe", 7: "swaahteethswaahkwe", 8: "palaanwaahkwe", 9: "nkotimeneehkwaahkwe"}
THOUSANDS = {1: "mataathswaahkwe"}
RULES = {"teen_prefix": "mataathswi", "teen_suffix": "aasi"}

# 1. GENERATE THE "HOTWORD" PROMPT
# This is what we feed Whisper to bias its "ears"
lexemes = list(ONES.values()) + list(TENS.values()) + list(HUNDREDS.values()) + list(THOUSANDS.values()) + [RULES["teen_prefix"], RULES["teen_suffix"]]
# Create a unique, comma-separated string for the prompt
WHISPER_PROMPT = ", ".join(sorted(list(set(lexemes))))

# 2. THE RECURSIVE NUMBER BUILDER (For TMX generation)
def get_myaamia_number(n):
    if n == 0: return "moochi"
    if n < 10: return ONES[n]
    if n == 10: return "mataathswi moochiaasi"
    if n < 20: return f"{RULES['teen_prefix']} {ONES[n-10]}{RULES['teen_suffix']}"
    
    parts = []
    # Handle Thousands (Basic)
    if n >= 1000:
        th = n // 1000
        parts.append(THOUSANDS.get(1, "mataathswaahkwe")) # Simplistic for 1k-9k
        n %= 1000
    # Handle Hundreds
    if n >= 100:
        h = n // 100
        parts.append(HUNDREDS[h])
        n %= 100
    # Handle Tens
    if n >= 20:
        t = n // 10
        parts.append(TENS[t])
        n %= 10
    # Handle Remainder
    if n > 0:
        parts.append(ONES[n])
        
    return " ".join(parts)

# Example: print(get_myaamia_number(134)) 
# Output: nkotwaahkwe nihswi mateeni niiwi