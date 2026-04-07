# !/usr/bin/env python3
"""
Extract Sauk dictionary data from PDF.
"""
import pdfplumber
import pandas as pd
import re
from pathlib import Path
import json

def extract_pdf_entries(pdf_path):
    """
    Extract dictionary entries from PDF.
    This needs customization based on the PDF's actual format.
    """
    entries = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Extracting from {len(pdf.pages)} pages...")
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
                
            # Split into lines
            lines = text.split('\n')
            
            # TODO: Customize this based on the PDF's actual structure
            # You'll need to inspect the PDF and adjust the parsing logic
            
            current_entry = {}
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Example pattern: "word  meaning"
                if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s{2,}', line):
                    # This looks like a headword followed by definition
                    parts = re.split(r'\s{2,}', line)
                    if len(parts) >= 2:
                        current_entry = {
                            'headword': parts[0],
                            'definition': ' '.join(parts[1:]),
                            'page': page_num + 1
                        }
                        entries.append(current_entry)
                else:
                    # Continuation of previous entry
                    if current_entry and 'definition' in current_entry:
                        current_entry['definition'] += ' ' + line
            
            print(f"  Page {page_num + 1}: {len(entries)} entries so far")
    
    return entries

def save_extracted_data(entries, output_format='csv'):
    """Save extracted entries in various formats."""
    df = pd.DataFrame(entries)
    
    # Save in multiple formats
    filename_base = "sauk_dictionary"
    
    if output_format in ['csv', 'all']:
        df.to_csv(f"{filename_base}.csv", index=False, encoding='utf-8')
        print(f"Saved CSV to {filename_base}.csv")
    
    if output_format in ['json', 'all']:
        df.to_json(f"{filename_base}.json", orient='records', force_ascii=False)
        print(f"Saved JSON to {filename_base}.json")
    
    if output_format in ['xlsx', 'all']:
        df.to_excel(f"{filename_base}.xlsx", index=False)
        print(f"Saved Excel to {filename_base}.xlsx")
    
    # Create TMX format for translation
    if output_format in ['tmx', 'all']:
        with open(f"{filename_base}.tmx", "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<tmx version="1.4">\n')
            f.write('  <header\n')
            f.write('    creationtool="pdf_extractor"\n')
            f.write('    creationtoolversion="1.0"\n')
            f.write('    datatype="plaintext"\n')
            f.write('    segtype="sentence"\n')
            f.write('    adminlang="en"\n')
            f.write('    srclang="sauk"\n')
            f.write('    o-tmf="plain"\n')
            f.write('  >\n')
            f.write('  </header>\n')
            f.write('  <body>\n')
            
            for entry in entries[:100]:  # Limit for demo
                if 'headword' in entry and 'definition' in entry:
                    f.write(f'    <tu>\n')
                    f.write(f'      <tuv lang="sauk">\n')
                    f.write(f'        <seg>{entry["headword"]}</seg>\n')
                    f.write(f'      </tuv>\n')
                    f.write(f'      <tuv lang="en">\n')
                    f.write(f'        <seg>{entry["definition"]}</seg>\n')
                    f.write(f'      </tuv>\n')
                    f.write(f'    </tu>\n')
            
            f.write('  </body>\n')
            f.write('</tmx>\n')
        print(f"Saved TMX to {filename_base}.tmx")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract Sauk dictionary from PDF')
    parser.add_argument('pdf_file', help='Path to PDF dictionary')
    parser.add_argument('--format', choices=['csv', 'json', 'xlsx', 'tmx', 'all'],
                       default='all', help='Output format')
    args = parser.parse_args()
    
    # Extract entries
    entries = extract_pdf_entries(args.pdf_file)
    print(f"✅ Extracted {len(entries)} entries")
    
    # Save in various formats
    save_extracted_data(entries, args.format)
    
    # Show preview
    print("\n🔍 Preview of first 5 entries:")
    for i, entry in enumerate(entries[:5]):
        print(f"{i+1}. {entry.get('headword', 'N/A')}: {entry.get('definition', 'N/A')[:100]}...")

if __name__ == "__main__":
    main()
