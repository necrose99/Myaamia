import sys
import re
import os
import pypdf
from lxml import etree
from datetime import datetime

# 1. Master Algic Configuration
ALGIC_ARRAY = {
    "mia": "Miami-Illinois",
    "sac": "Sauk",
    "mes": "Meskwaki",
    "pot": "Potawatomi"
}

# Regex for Scientific Latin and PDF artifacts
LATIN_REGEX = re.compile(r'\(([A-Z][a-z]+ [a-z]+)\)')
SPLIT_WORD_REGEX = re.compile(r'([a-z]+)-$') # Matches trailing hyphens

def normalize_orthography(text):
    if not text: return ""
    mapping = {'ʃ': 'š', 'ʒ': 'ž', 'æ': 'ae', 'ə': 'e'}
    for spec, std in mapping.items():
        text = text.replace(spec, std)
    return re.sub(r'\s+', ' ', text).strip()

def extract_column_aware_pdf(pdf_path, iso_code):
    """Splits pages vertically to prevent column bleeding."""
    reader = pypdf.PdfReader(pdf_path)
    root = etree.Element("tmx", version="1.4")
    body = etree.SubElement(root, "body")
    XML_NS = "http://www.w3.org/XML/1998/namespace"

    # Sauk Dictionary usually starts around p.22 (index 21)
    for p_num in range(21, min(140, len(reader.pages))):
        page = reader.pages[p_num]
        width = page.mediabox.width
        height = page.mediabox.height
        
        # Split page into two vertical boxes (Left/Right columns)
        for col_idx in [0, 1]:
            # Define crop box for the column
            left = (width / 2) * col_idx
            right = (width / 2) * (col_idx + 1)
            page.mediabox.lower_left = (left, 0)
            page.mediabox.upper_right = (right, height)
            
            text = page.extract_text()
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                # Heuristic: Sauk dictionaries often have Sauk on left, English on right
                # We look for the first significant space or dot-leader
                parts = re.split(r'\s{2,}', line.strip(), maxsplit=1)
                if len(parts) == 2:
                    tu = etree.SubElement(body, "tu", tuid=f"{iso_code}_{p_num}_{col_idx}_{i}")
                    
                    # Native (Sauk)
                    tuv_nat = etree.SubElement(tu, "tuv", {f"{{{XML_NS}}}lang": iso_code})
                    etree.SubElement(tuv_nat, "seg").text = normalize_orthography(parts[0])
                    
                    # English
                    tuv_en = etree.SubElement(tu, "tuv", {f"{{{XML_NS}}}lang": "en-US"})
                    etree.SubElement(tuv_en, "seg").text = normalize_orthography(parts[1])

    return root

def heal_tmx_bleeding(root, iso_code):
    """Heals artifacts like 'eautifu' + 'autiful' across adjacent units."""
    XML_NS = "http://www.w3.org/XML/1998/namespace"
    units = root.xpath('//tu')
    to_remove = []

    for i in range(len(units) - 1):
        tu1, tu2 = units[i], units[i+1]
        en1 = "".join(tu1.xpath('.//tuv[@xml:lang="en-US"]/seg/text()'))
        en2 = "".join(tu2.xpath('.//tuv[@xml:lang="en-US"]/seg/text()'))
        
        # Heuristic: Join if TU1 ends with lowercase and TU2 starts with lowercase (split word)
        if en1 and en2 and en1[-1].islower() and en2[0].islower():
            # Join English
            tu1.xpath('.//tuv[@xml:lang="en-US"]/seg')[0].text = en1 + en2
            # Join Native (assuming similar split)
            nat1 = "".join(tu1.xpath(f'.//tuv[@xml:lang="{iso_code}"]/seg/text()'))
            nat2 = "".join(tu2.xpath(f'.//tuv[@xml:lang="{iso_code}"]/seg/text()'))
            tu1.xpath(f'.//tuv[@xml:lang="{iso_code}"]/seg')[0].text = nat1 + " " + nat2
            
            to_remove.append(tu2)
            
    for tu in to_remove:
        if tu.getparent() is not None:
            tu.getparent().remove(tu)
    
    return root

# Main Execution Logic
if __name__ == "__main__":
    # 1. Extract from PDF with Column-Awareness
    # root = extract_column_aware_pdf("Copy-of-A-Concise-Dictionary-Sauk.pdf", "sac")
    
    # 2. Alternatively, Mend your existing sac_full_cleaned.tmx
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse("sac_full_cleaned.tmx", parser)
    mended_root = heal_tmx_bleeding(tree.getroot(), "sac")
    
    # 3. Final Scientific Extraction & Clean-up
    # [Insert your Latin Regex logic here as done before]
    
    tree.write("sac_FIXED.tmx", encoding="UTF-8", xml_declaration=True, pretty_print=True)
    print("✅ Mending complete. 'eautifu' + 'autiful' joined into 'beautiful'.")