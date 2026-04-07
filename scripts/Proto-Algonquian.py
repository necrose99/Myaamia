# !/usr/bin/env python3
"""
Proto-Algonquian to TMX/FLEX/EAF Exporter
Pulls data from https://protoalgonquian.atlas-ling.ca/ and exports to standard formats
"""

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from xml.dom import minidom
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
import argparse
from typing import Dict, List, Optional, Tuple
import re
import time

class ProtoAlgonquianExporter:
    """Export Proto-Algonquian data to TMX, EAF, and FLEX formats"""
    
    def __init__(self, 
                 db_path: str = 'proto_algonquian.db',
                 base_url: str = "https://protoalgonquian.atlas-ling.ca"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.base_url = base_url
        
        # Initialize database
        self._init_database()
        
        # Cache for PALA data
        self.pala_cache = {}
        self._load_cache()
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS proto_entries (
                id TEXT PRIMARY KEY,
                proto_form TEXT,
                meaning TEXT,
                phonology TEXT,
                animacy TEXT,
                notes TEXT,
                harvested_at TIMESTAMP,
                raw_data TEXT
            );
            
            CREATE TABLE IF NOT EXISTS descendants (
                id TEXT PRIMARY KEY,
                proto_id TEXT,
                language TEXT,
                form TEXT,
                notes TEXT,
                FOREIGN KEY (proto_id) REFERENCES proto_entries(id)
            );
            
            CREATE TABLE IF NOT EXISTS relations (
                id TEXT PRIMARY KEY,
                source_id TEXT,
                target_id TEXT,
                relation_type TEXT,
                confidence REAL,
                source TEXT,
                FOREIGN KEY (source_id) REFERENCES proto_entries(id),
                FOREIGN KEY (target_id) REFERENCES proto_entries(id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_descendants_language ON descendants(language);
            CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(relation_type);
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_cache(self):
        """Load cache from file"""
        cache_file = self.db_path.with_suffix('.cache.json')
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                self.pala_cache = json.load(f)
    
    def _save_cache(self):
        """Save cache to file"""
        cache_file = self.db_path.with_suffix('.cache.json')
        with open(cache_file, 'w') as f:
            json.dump(self.pala_cache, f, indent=2)
    
    def harvest_pala(self, 
                    max_entries: int = 100,
                    languages: List[str] = None):
        """
        Harvest Proto-Algonquian entries from PALA
        
        Args:
            max_entries: Maximum number of entries to harvest
            languages: Filter by language codes (e.g., ['esx', 'kic'])
        """
        if languages is None:
            languages = ['esx', 'kic', 'oka', 'mjx']  # Algic languages
        
        all_entries = []
        page = 1
        count = 0
        
        while count < max_entries:
            url = f"{self.base_url}/search?page={page}"
            print(f"🔍 Harvesting page {page}...")
            
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find entries on page
                entries = soup.find_all('div', class_='entry')
                if not entries:
                    break
                
                for entry in entries[:10]:  # Limit per page
                    if count >= max_entries:
                        break
                    
                    proto_data = self._parse_entry(entry)
                    if proto_data:
                        all_entries.append(proto_data)
                        count += 1
                
                page += 1
                time.sleep(2)  # Be polite
                
            except Exception as e:
                print(f"⚠️  Error harvesting page {page}: {e}")
                break
        
        print(f"✅ Harvested {len(all_entries)} Proto-Algonquian entries")
        return all_entries
    
    def _parse_entry(self, entry_elem) -> Optional[Dict]:
        """Parse a Proto-Algonquian entry"""
        try:
            proto_form = entry_elem.find('h3', class_='proto-form').text.strip()
            meaning = entry_elem.find('div', class_='meaning').text.strip()
            
            # Extract phonology
            phonology_elem = entry_elem.find('div', class_='phonology')
            phonology = phonology_elem.text.strip() if phonology_elem else ''
            
            # Extract animacy
            animacy_elem = entry_elem.find('div', class_='animacy')
            animacy = animacy_elem.text.strip() if animacy_elem else ''
            
            # Extract notes
            notes_elem = entry_elem.find('div', class_='notes')
            notes = notes_elem.text.strip() if notes_elem else ''
            
            # Extract descendants
            descendants = []
            for descendant_row in entry_elem.find_all('tr')[1:]:  # Skip header
                cols = descendant_row.find_all('td')
                if len(cols) >= 2:
                    language = cols[0].text.strip()
                    form = cols[1].text.strip()
                    notes = cols[2].text.strip() if len(cols) > 2 else ''
                    descendants.append({
                        'language': language,
                        'form': form,
                        'notes': notes
                    })
            
            return {
                'proto_form': proto_form,
                'meaning': meaning,
                'phonology': phonology,
                'animacy': animacy,
                'notes': notes,
                'descendants': descendants,
                'harvested_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️  Error parsing entry: {e}")
            return None
    
    def save_to_database(self, entries: List[Dict]):
        """Save entries to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for entry in entries:
            cursor.execute('''
                INSERT OR IGNORE INTO proto_entries 
                (id, proto_form, meaning, phonology, animacy, notes, harvested_at, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid5(uuid.NAMESPACE_URL, entry['proto_form'])),
                entry['proto_form'],
                entry['meaning'],
                entry['phonology'],
                entry['animacy'],
                entry['notes'],
                entry['harvested_at'],
                json.dumps(entry, ensure_ascii=False)
            ))
            
            proto_id = str(uuid.uuid5(uuid.NAMESPACE_URL, entry['proto_form']))
            
            # Save descendants
            for descendant in entry['descendants']:
                cursor.execute('''
                    INSERT OR IGNORE INTO descendants 
                    (id, proto_id, language, form, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    str(uuid.uuid5(uuid.NAMESPACE_URL, f"{proto_id}{descendant['language']}")),
                    proto_id,
                    descendant['language'],
                    descendant['form'],
                    descendant['notes']
                ))
        
        conn.commit()
        conn.close()
        print(f"💾 Saved {len(entries)} entries to database")
    
    def export_tmx(self,
                  output_path: str,
                  source_lang: str = 'proto-alg',
                  target_lang: str = 'eng'):
        """Export Proto-Algonquian data to TMX"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pe.proto_form, pe.meaning, pe.phonology, 
                   d.language, d.form, d.notes
            FROM proto_entries pe
            JOIN descendants d ON pe.id = d.proto_id
            WHERE pe.meaning IS NOT NULL
            ORDER BY pe.proto_form
        ''')
        
        tus = []
        for row in cursor.fetchall():
            tus.append({
                'source': row[0],
                'source_meaning': row[1],
                'source_phonology': row[2],
                'target_language': row[3],
                'target': row[4],
                'target_notes': row[5]
            })
        
        conn.close()
        
        # Build TMX
        body_xml = ''
        for i, tu in enumerate(tus):
            source_escaped = self._escape_xml(tu['source'])
            target_escaped = self._escape_xml(tu['target'])
            
            props = ''
            if tu['source_meaning']:
                props += f'<prop type="meaning">{self._escape_xml(tu["source_meaning"])}</prop>'
            if tu['source_phonology']:
                props += f'<prop type="phonology">{self._escape_xml(tu["source_phonology"])}</prop>'
            if tu['target_notes']:
                props += f'<prop type="notes">{self._escape_xml(tu["target_notes"])}</prop>'
            
            body_xml += f'''
            <tu>
                <prop type="id">{i}</prop>
                {props}
                <tuv xml:lang="{source_lang}">
                    <seg>{source_escaped}</seg>
                </tuv>
                <tuv xml:lang="{target_lang}">
                    <seg>{target_escaped}</seg>
                </tuv>
            </tu>'''
        
        tmx_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<tmx version="1.4">
    <header>
        <srclang>{source_lang}</srclang>
        <targetlang>{target_lang}</targetlang>
        <charset>UTF-8</charset>
        <creationtool>proto-algonquian-exporter</creationtool>
        <creationtoolversion>1.0</creationtoolversion>
        <date>{datetime.now().strftime('%Y%m%d%H%M%S')}</date>
        <datasource>Proto-Algonquian Lexicon</datasource>
    </header>
    <body>
        {body_xml}
    </body>
</tmx>'''
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(tmx_content, encoding='utf-8')
        
        return str(output_path)
    
    def export_flex(self, output_path: str):
        """Export to FLEX format"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pe.proto_form, pe.meaning, pe.phonology, pe.animacy, pe.notes,
                   d.language, d.form, d.notes as descendant_notes
            FROM proto_entries pe
            LEFT JOIN descendants d ON pe.id = d.proto_id
            ORDER BY pe.proto_form, d.language
        ''')
        
        entries = []
        current_proto = None
        current_entry = None
        
        for row in cursor.fetchall():
            proto_form, meaning, phonology, animacy, notes, lang, form, desc_notes = row
            
            if proto_form != current_proto:
                if current_entry:
                    entries.append(current_entry)
                current_entry = {
                    'proto_form': proto_form,
                    'meaning': meaning,
                    'phonology': phonology,
                    'animacy': animacy,
                    'notes': notes,
                    'descendants': []
                }
                current_proto = proto_form
            
            if form:
                current_entry['descendants'].append({
                    'language': lang,
                    'form': form,
                    'notes': desc_notes
                })
        
        if current_entry:
            entries.append(current_entry)
        
        conn.close()
        
        # Build FLEX XML
        entries_xml = []
        for entry in entries:
            lexical_xml = f'<LexemeForm>{self._escape_xml(entry["proto_form"])}</LexemeForm>'
            if entry['phonology']:
                lexical_xml += f'<Pronunciation>{self._escape_xml(entry["phonology"])}</Pronunciation>'
            
            sense_xml = f'<Sense>{self._escape_xml(entry["meaning"])}</Sense>'
            
            examples_xml = ''
            for desc in entry['descendants']:
                examples_xml += f'''
                <Example>
                    <ExampleForm>{self._escape_xml(desc["form"])}</ExampleForm>
                    <Translation>{self._escape_xml(desc["language"])}: {self._escape_xml(desc["notes"])}</Translation>
                </Example>'''
            
            entry_xml = f'''<LexEntry id="{uuid.uuid4().hex}">
                <LexEntry>{self._escape_xml(entry["proto_form"])}</LexEntry>
                {lexical_xml}
                <GramInfo>{self._escape_xml(entry["animacy"])}</GramInfo>
                <Senses>
                    <Sense>{sense_xml}</Sense>
                </Senses>
                {examples_xml}
                <Metadata>
                    <Source>Proto-Algonquian Lexicon (PALA)</Source>
                    <Notes>{self._escape_xml(entry["notes"])}</Notes>
                </Metadata>
            </LexEntry>'''
            
            entries_xml.append(entry_xml)
        
        flex_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<FLEX_Document xmlns="http://forlang.sourceforge.net/flex/1.0">
    <Lexicon>
        <LexEntries>
            {"".join(entries_xml)}
        </LexEntries>
    </Lexicon>
</FLEX_Document>'''
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(flex_xml, encoding='utf-8')
        
        return str(output_path)
    
    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters"""
        if not text:
            return ''
        return (text
                .replace('&', '&')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))

def main():
    parser = argparse.ArgumentParser(
        description='Export Proto-Algonquian data to TMX/FLEX/EAF formats'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Harvest command
    harvest_parser = subparsers.add_parser('harvest', help='Harvest PALA entries')
    harvest_parser.add_argument('--db', default='proto_algonquian.db', help='Database file')
    harvest_parser.add_argument('--max', type=int, default=100, help='Max entries')
    
    # Export TMX command
    tmx_parser = subparsers.add_parser('export-tmx', help='Export to TMX')
    tmx_parser.add_argument('--db', default='proto_algonquian.db', help='Database file')
    tmx_parser.add_argument('--output', required=True, help='Output TMX file')
    tmx_parser.add_argument('--source', default='proto-alg', help='Source language')
    tmx_parser.add_argument('--target', default='eng', help='Target language')
    
    # Export FLEX command
    flex_parser = subparsers.add_parser('export-flex', help='Export to FLEX')
    flex_parser.add_argument('--db', default='proto_algonquian.db', help='Database file')
    flex_parser.add_argument('--output', required=True, help='Output FLEX file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.error('No command specified. Use --help to see options.')
    
    exporter = ProtoAlgonquianExporter(db_path=args.db)
    
    if args.command == 'harvest':
        entries = exporter.harvest_pala(max_entries=args.max)
        exporter.save_to_database(entries)
    
    elif args.command == 'export-tmx':
        exporter.export_tmx(
            output_path=args.output,
            source_lang=args.source,
            target_lang=args.target
        )
    
    elif args.command == 'export-flex':
        exporter.export_flex(output_path=args.output)

if __name__ == '__main__':
    import time
    main()
