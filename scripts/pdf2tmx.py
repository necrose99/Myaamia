import pdfplumber
import xml.etree.ElementTree as ET
import os
import re

def clean_for_search(text):
    """Normalizes IPA to basic Latin for easier SQL querying."""
    if not text: return ""
    # Standard Algic phonetic mapping
    mapping = {
        'ʃ': 'š', 'ʒ': 'ž', 'tʃ': 'č', 'dʒ': 'ǰ',
        'θ': 'th', 'æ': 'ae', 'ə': 'e', 'm̃': 'm',
        'ñ': 'n', 'w̃': 'w'
    }
    for ipa, lat in mapping.items():
        text = text.replace(ipa, lat)
    return text

def pdf_to_tmx_full(pdf_path, output_tmx):
    # 1. TMX Boilerplate
    root = ET.Element("tmx", version="1.4")
    header = ET.SubElement(root, "header", {
        "creationtool": "Algic-IPA-Muncher",
        "segtype": "phrase",
        "adminlang": "en-US",
        "srclang": "en-US",
        "datatype": "PlainText"
    })
    body = ET.SubElement(root, "body")

    count = 0
    print(f"🚀 Munching PDF: {pdf_path}...")

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            # We use 'text' strategy if the PDF doesn't have visible lines
            # If the PDF is a clean grid, use 'lines'
            table = page.extract_table(table_settings={
                "vertical_strategy": "text", 
                "horizontal_strategy": "text",
                "snap_tolerance": 3
            })
            
            if table:
                for row in table:
                    # Filter out empty or single-column rows
                    if not row or len(row) < 2:
                        continue
                    
                    # Row[0] = Sauk (IPA), Row[1] = English
                    raw_sauk = row[0].strip() if row[0] else ""
                    raw_eng = row[1].strip() if row[1] else ""

                    if raw_sauk and raw_eng:
                        tu = ET.SubElement(body, "tu", tuid=f"sac_wb_{i}_{count}")
                        
                        # Note stores the original IPA for the TTS engine
                        ET.SubElement(tu, "note").text = f"Original IPA: {raw_sauk}"
                        
                        # English TUV
                        tuv_en = ET.SubElement(tu, "tuv")
                        tuv_en.set("{http://www.w3.org/XML/1998/namespace}lang", "en-US")
                        ET.SubElement(tuv_en, "seg").text = raw_eng
                        
                        # Sauk TUV (Preserving IPA)
                        tuv_sac = ET.SubElement(tu, "tuv")
                        tuv_sac.set("{http://www.w3.org/XML/1998/namespace}lang", "sac")
                        ET.SubElement(tuv_sac, "seg").text = raw_sauk
                        
                        count += 1

    # 2. Save with UTF-8 Integrity
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_tmx, encoding="utf-8", xml_declaration=True)
    
    print(f"✨ Created {output_tmx} with {count} entries.")

if __name__ == "__main__":
    pdf_to_tmx_full('finalsaukworkbook.pdf', 'sac_ipa_shard.tmx')
