# tmx_to_babeledit_algonquian_full.py
import json
from pathlib import Path
from collections import defaultdict

# pip install translate-toolkit
from translate.storage.tmx import tmxfile

# Complete language mapping (TMX code → Display name in BabelEdit)
LANGUAGE_MAP = {
    # Plains
    "bft": "Blackfoot",
    "arp": "Arapaho",
    "ats": "Gros Ventre",
    "chy": "Cheyenne",
    # Central
    "men": "Menominee",
    "cre": "Cree",
    "csw": "Swampy Cree",
    "crj": "Southern East Cree",
    "atj": "Atikamekw",
    "pot": "Potawatomi",
    "oji": "Ojibwe",
    "otw": "Ottawa",
    "ciw": "Chippewa",
    "mia": "Miami-Illinois (Myaamia)",   # Your main mia code
    "sac": "Meskwaki (Fox)",
    "kic": "Kickapoo (US)",
    "sha": "Shawnee",
    # Eastern
    "mic": "Mi'kmaq",
    "abe": "Western Abenaki",
    "aaq": "Eastern Abnaki",
    "mal": "Maliseet-Passamaquoddy",
    "moo": "Mohegan-Pequot",
    "mua": "Munsee",
    "unm": "Unami",
    # Proto
    "alg-x-proto": "Proto-Algonquian",
    # Supervisor languages
    "en": "English",
    "es": "Spanish",
    "la": "Latin (Scientific / Botanical)",
    "fr": "French",
    "fr_ca": "Canadian French",
    "fr_old": "Old French (1600s-style / Historical)",
    # Kickapoo variants
    "kick_us": "Kickapoo (US)",
    "kic_mx": "Kickapoo (Mexico)",
}

def tmx_to_json(tmx_path: str, output_dir: str = "algonquian_babeledit_full"):
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    with open(tmx_path, 'rb') as fin:
        tmx = tmxfile(fin)

    translations = defaultdict(dict)

    for unit in tmx.units:
        key = unit.getid() or unit.source
        if not key:
            continue
        for lang_code, text in unit.items():
            text = text.strip()
            if text:
                translations[lang_code][key] = text

    created = []
    for lang_code, data in translations.items():
        if lang_code == "kic":
            # Duplicate for US/MX variants
            for variant, display in [("kick_us", "Kickapoo (US)"), ("kic_mx", "Kickapoo (Mexico)")]:
                safe = variant.replace('-', '_').lower()
                path = output_dir / f"{safe}.json"
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                created.append((path.name, variant, display))
                print(f"Created: {path.name} → {display} ({len(data)} strings)")
        else:
            safe = lang_code.replace('-', '_').lower()
            path = output_dir / f"{safe}.json"
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            display = LANGUAGE_MAP.get(lang_code, lang_code)
            created.append((path.name, lang_code, display))
            print(f"Created: {path.name} → {display} ({len(data)} strings)")

    # Create empty supervisor files so they appear in BabelEdit
    supervisors = [
        ("en", "English"),
        ("es", "Spanish"),
        ("la", "Latin (Scientific / Botanical)"),
        ("fr", "French"),
        ("fr_ca", "Canadian French"),
        ("fr_old", "Old French (1600s-style / Historical)"),
    ]
    for code, name in supervisors:
        if code not in translations:
            safe = code.replace('-', '_').lower()
            path = output_dir / f"{safe}.json"
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            created.append((path.name, code, name))
            print(f"Created empty supervisor: {path.name} → {name}")

    print(f"\n✅ All done! {len(created)} files created in '{output_dir}/'")

    print("\n=== BabelEdit Setup Recommendations ===")
    print("1. New Project → Generic JSON → Add the whole folder")
    print("2. Set **English (en)** as Primary/Source language")
    print("3. For custom languages (including fr_ca, fr_old, mia, alg-x-proto, etc.):")
    print("   - When you see 'Language code not found?' → click it → New")
    print("   - Enter the Code and Name from the list above")
    print("   - Base spell-checker / Machine Translation:")
    print("       • Canadian French (fr_ca) → base on 'fr' or 'fr-CA'")
    print("       • Old French (fr_old)     → base on 'fr' (French)")
    print("       • Miami-Illinois (mia)    → base on 'en'")
    print("       • Latin (la)              → base on 'la'")
    print("4. Use **fr_old** for 1600s–1700s French records related to Myaamia and cousin tribes")
    print("   → Great for cross-referencing old Jesuit/missionary texts with modern Myaamia terms")
    print("5. You can copy terms easily between fr, fr_ca, and fr_old inside BabelEdit")

    return created


if __name__ == "__main__":
    tmx_file = "your_algonquian.tmx"   # ← Update with your actual TMX filename
    tmx_to_json(tmx_file, output_dir="algonquian_babeledit_full")
