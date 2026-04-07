# !/usr/bin/env python3
"""
OLAC to TMX/EAF/FLEX Exporter
Pulls linguistic data from OLAC repositories and exports to standard formats
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

class OLACExporter:
    """Export OLAC data to TMX, EAF, and FLEX formats"""
    
    def __init__(self, 
                 db_path: str = 'olac_data.db',
                 olac_repos: List[str] = None):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Default OLAC repositories with Algic language data
        if olac_repos is None:
            self.olac_repos = [
                'https://olac.org/repository/crdo/',
                'https://olac.org/repository/mpi/',
                'https://olac.org/repository/asu/',
                'https://olac.org/repository/uchicago/'
            ]
        
        # Initialize database
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for OLAC data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS olac_records (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                language TEXT,
                subject TEXT,
                type TEXT,
                format TEXT,
                identifier TEXT,
                rights TEXT,
                publisher TEXT,
                contributor TEXT,
                coverage TEXT,
                relation TEXT,
                source TEXT,
                language_code TEXT,
                oai_identifier TEXT,
                harvested_at TIMESTAMP,
                raw_xml TEXT
            );
            
            CREATE TABLE IF NOT EXISTS linguistic_data (
                id TEXT PRIMARY KEY,
                record_id TEXT,
                word TEXT,
                ipa TEXT,
                pos TEXT,
                translation TEXT,
                language_code TEXT,
                concept TEXT,
                confidence REAL,
                FOREIGN KEY (record_id) REFERENCES olac_records(id)
            );
            
            CREATE TABLE IF NOT EXISTS examples (
                id TEXT PRIMARY KEY,
                lexical_id TEXT,
                sentence TEXT,
                translation TEXT,
                source TEXT,
                context TEXT,
                FOREIGN KEY (lexical_id) REFERENCES linguistic_data(id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_olac_language ON olac_records(language_code);
            CREATE INDEX IF NOT EXISTS idx_linguistic_word ON linguistic_data(word);
        ''')
        
        conn.commit()
        conn.close()
    
    def harvest_olac(self, 
                    max_records: int = 100,
                    languages: List[str] = None):
        """
        Harvest OLAC records from repositories
        
        Args:
            max_records: Maximum number of records to harvest
            languages: Filter by language codes (e.g., ['esx', 'kic'])
        """
        if languages is None:
            languages = ['esx', 'kic', 'oka', 'mjx']  # Algic languages
        
        all_records = []
        
        for repo in self.olac_repos:
            print(f"🔍 Harvesting from {repo}...")
            
            # Harvest using OLAC OAI-PMH
            records = self._harvest_oai_pmh(repo, languages, max_records)
            all_records.extend(records)
            
            # Be polite and rate limit
            time.sleep(2)
        
        print(f"✅ Harvested {len(all_records)} records")
        return all_records
    
    def _harvest_oai_pmh(self, 
                        repo_url: str,
                        languages: List[str],
                        max_records: int) -> List[Dict]:
        """Harvest records using OAI-PMH"""
        records = []
        token = None
        
        for i in range(10):  # Max 10 requests
            if token:
                params = {'resumptionToken': token}
            else:
                params = {
                    'verb': 'ListRecords',
                    'metadataPrefix': 'olac',
                    'set': f'language:{",".join(languages)}'
                }
            
            try:
                response = requests.get(repo_url, params=params, timeout=30)
                response.raise_for_status()
                
                # Parse OAI-PMH response
                root = ET.fromstring(response.content)
                
                # Extract records
                for record_elem in root.findall('.//{http://www.openarchives.org/OAI/2.0/}record'):
                    record = self._parse_olac_record(record_elem)
                    if record:
                        records.append(record)
                
                # Check for resumption token
                token_elem = root.find('.//{http://www.openarchives.org/OAI/2.0/}resumptionToken')
                token = token_elem.text if token_elem is not None and token_elem.text else None
                
                if not token or len(records) >= max_records:
                    break
                    
            except Exception as e:
                print(f"⚠️  Error harvesting from {repo_url}: {e}")
                break
        
        return records[:max_records]
    
    def _parse_olac_record(self, record_elem) -> Optional[Dict]:
        """Parse an OLAC record"""
        try:
            header = record_elem.find('{http://www.openarchives.org/OAI/2.0/}header')
            if header is None or header.find('identifier') is None:
                return None
            
            identifier = header.find('identifier').text
            
            metadata_elem = record_elem.find('{http://www.openarchives.org/OAI/2.0/}metadata')
            if metadata_elem is None:
                return None
            
            # Parse OLAC elements
            olac_ns = {'olac': 'http://www.language-archives.org/OLAC/1.1/'}
            
            title = self._get_text(metadata_elem, 'dc:title')
            description = self._get_text(metadata_elem, 'dc:description')
            language = self._get_text(metadata_elem, 'dc:language')
            subject = self._get_text(metadata_elem, 'dc:subject')
            record_type = self._get_text(metadata_elem, 'dc:type')
            format = self._get_text(metadata_elem, 'dc:format')
            oai_identifier = self._get_text(metadata_elem, 'olac:identifier')
            rights = self._get_text(metadata_elem, 'dc:rights')
            publisher = self._get_text(metadata_elem, 'dc:publisher')
            contributor = self._get_text(metadata_elem, 'dc:contributor')
            coverage = self._get_text(metadata_elem, 'dc:coverage')
            relation = self._get_text(metadata_elem, 'dc:relation')
            source = self._get_text(metadata_elem, 'dc:source')
            
            # Extract language code from OLAC language element
            language_code = self._extract_language_code(language) if language else None
            
            return {
                'id': str(uuid.uuid5(uuid.NAMESPACE_URL, identifier)),
                'title': title,
                'description': description,
                'language': language,
                'language_code': language_code,
                'subject': subject,
                'type': record_type,
                'format': format,
                'identifier': oai_identifier,
                'rights': rights,
                'publisher': publisher,
                'contributor': contributor,
                'coverage': coverage,
                'relation': relation,
                'source': source,
                'oai_identifier': oai_identifier,
                'harvested_at': datetime.now().isoformat(),
                'raw_xml': ET.tostring(metadata_elem, encoding='unicode')
            }
            
        except Exception as e:
            print(f"⚠️  Error parsing OLAC record: {e}")
            return None
    
    def _get_text(self, element, tag: str) -> str:
        """Get text from element with namespace"""
        found = element.find(f'.//{tag}')
        return found.text.strip() if found is not None and found.text else ''
    
    def _extract_language_code(self, language_text: str) -> str:
        """Extract ISO language code from OLAC language element"""
        # OLAC language can be in various formats
        # Try to extract ISO 639 code
        import re
        match = re.search(r'\b([a-z]{2,3})\b', language_text.lower())
        if match:
            return match.group(1)
        
        # Fallback to first part of language name
        return language_text.split(';')[0].split(',')[0].strip().lower()
    
    def save_to_database(self, records: List[Dict]):
        """Save harvested records to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT OR IGNORE INTO olac_records 
                (id, title, description, language, language_code, subject, type, 
                 format, identifier, rights, publisher, contributor, coverage, 
                 relation, source, oai_identifier, harvested_at, raw_xml)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record['id'], record['title'], record['description'],
                record['language'], record['language_code'], record['subject'],
                record['type'], record['format'], record['identifier'],
                record['rights'], record['publisher'], record['contributor'],
                record['coverage'], record['relation'], record['source'],
                record['oai_identifier'], record['harvested_at'], record['raw_xml']
            ))
        
        conn.commit()
        conn.close()
        print(f"💾 Saved {len(records)} records to database")
    
    def extract_linguistic_data(self):
        """Extract linguistic data from OLAC records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, language_code, subject, raw_xml
            FROM olac_records
            WHERE language_code IN ('esx', 'kic', 'oka', 'mjx')
        ''')
        
        for row in cursor.fetchall():
            record_id, title, description, lang_code, subject, raw_xml = row
            
            # Try to extract linguistic data from title/description
            self._extract_from_text(record_id, title, lang_code, 'title')
            self._extract_from_text(record_id, description, lang_code, 'description')
            
            # Try to parse OLAC XML for structured linguistic data
            self._extract_from_xml(record_id, raw_xml, lang_code)
        
        conn.commit()
        conn.close()
    
    def _extract_from_text(self, 
                          record_id: str,
                          text: str,
                          lang_code: str,
                          source: str):
        """Extract linguistic data from plain text"""
        # Look for word lists, translations, etc.
        patterns = {
            'word_list': r'Word[s]?\s*:\s*([^\n]+)',
            'translation': r'Translation[s]?\s*:\s*([^\n]+)',
            'ipa': r'IPA\s*:\s*/([^/]+)/',
            'example': r'Example[s]?\s*:\s*([^\n]+)'
        }
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Simple extraction - would need more sophisticated processing
                self._save_linguistic_item(
                    record_id=record_id,
                    word=match.strip(),
                    ipa='',
                    pos='',
                    translation='',
                    language_code=lang_code,
                    concept=pattern_name,
                    confidence=0.5,
                    source=source
                )
    
    def _extract_from_xml(self, 
                         record_id: str,
                         xml_content: str,
                         lang_code: str):
        """Extract linguistic data from OLAC XML"""
        try:
            root = ET.fromstring(xml_content)
            olac_ns = {'olac': 'http://www.language-archives.org/OLAC/1.1/'}
            
            # Look for OLAC extensions with linguistic data
            for extension in root.findall('.//olac:extension', olac_ns):
                if 'type' in extension.attrib:
                    ext_type = extension.attrib['type']
                    if ext_type.startswith('linguistic'):
                        # Extract data from linguistic extension
                        self._parse_linguistic_extension(record_id, extension, lang_code)
            
        except ET.ParseError:
            pass
    
    def _parse_linguistic_extension(self, 
                                   record_id: str,
                                   extension_elem,
                                   lang_code: str):
        """Parse OLAC linguistic extension"""
        # This would parse specific OLAC linguistic extensions
        # For now, just save the raw extension
        pass
    
    def _save_linguistic_item(self,
                            record_id: str,
                            word: str,
                            ipa: str,
                            pos: str,
                            translation: str,
                            language_code: str,
                            concept: str,
                            confidence: float,
                            source: str):
        """Save linguistic item to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        item_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{record_id}{word}{concept}"))
        
        cursor.execute('''
            INSERT OR IGNORE INTO linguistic_data 
            (id, record_id, word, ipa, pos, translation, language_code, concept, confidence, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item_id, record_id, word, ipa, pos, translation,
            language_code, concept, confidence, source
        ))
        
        conn.commit()
        conn.close()
    
    def export_tmx(self,
                  output_path: str,
                  source_lang: str,
                  target_lang: str,
                  min_confidence: float = 0.7):
        """Export linguistic data to TMX format"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ld1.word, ld1.ipa, ld1.pos, 
                   ld2.word as translation, ld2.ipa as target_ipa,
                   c1.label as concept, c2.label as translation_concept,
                   r.confidence, r.source
            FROM linguistic_data ld1
            JOIN relations r ON ld1.id = r.source_id
            JOIN linguistic_data ld2 ON r.target_id = ld2.id
            JOIN concepts c1 ON ld1.concept_id = c1.id
            JOIN concepts c2 ON ld2.concept_id = c2.id
            WHERE ld1.language_code = ? 
              AND ld2.language_code = ?
              AND r.relation_type = 'translation'
              AND r.confidence >= ?
        ''', (source_lang, target_lang, min_confidence))
        
        tus = []
        for row in cursor.fetchall():
            tus.append({
                'source': row[0],
                'source_ipa': row[1],
                'source_pos': row[2],
                'target': row[3],
                'target_ipa': row[4],
                'concept': row[5],
                'translation_concept': row[6],
                'confidence': row[7],
                'sources': [row[8]]
            })
        
        conn.close()
        
        # Build TMX
        return self._build_tmx(tus, source_lang, target_lang, output_path)
    
    def _build_tmx(self,
                  tus: List[Dict],
                  source_lang: str,
                  target_lang: str,
                  output_path: str) -> str:
        """Build TMX file"""
        body_xml = ''
        for i, tu in enumerate(tus):
            source_escaped = self._escape_xml(tu['source'])
            target_escaped = self._escape_xml(tu['target'])
            
            props = ''
            if tu['source_ipa']:
                props += f'<prop type="ipa">{self._escape_xml(tu["source_ipa"])}</prop>'
            if tu['source_pos']:
                props += f'<prop type="pos">{self._escape_xml(tu["source_pos"])}</prop>'
            if tu['confidence'] < 1.0:
                props += f'<prop type="confidence">{tu["confidence"]}</prop>'
            
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
        <creationtool>olac-exporter</creationtool>
        <creationtoolversion>1.0</creationtoolversion>
        <date>{datetime.now().strftime('%Y%m%d%H%M%S')}</date>
        <datasource>OLAC Harvest</datasource>
    </header>
    <body>
        {body_xml}
    </body>
</tmx>'''
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(tmx_content, encoding='utf-8')
        
        return str(output_path)
    
    def export_eaf(self,
                  output_path: str,
                  language: str,
                  include_all: bool = True):
        """Export annotations to EAF format"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if include_all:
            cursor.execute('''
                SELECT DISTINCT m.file_path, m.duration, m.width, m.height
                FROM media_files m
                JOIN annotations a ON m.id = a.media_id
                WHERE a.language = ?
            ''', (language,))
        else:
            cursor.execute('''
                SELECT DISTINCT m.file_path, m.duration, m.width, m.height
                FROM media_files m
                JOIN annotations a ON m.id = a.media_id
                JOIN linguistic_data ld ON a.lexical_id = ld.id
                WHERE a.language = ? AND ld.concept_id IS NOT NULL
            ''', (language,))
        
        media_files = []
        for row in cursor.fetchall():
            media_files.append({
                'id': f'media_{uuid.uuid4().hex[:8]}',
                'path': row[0],
                'duration': row[1],
                'width': row[2],
                'height': row[3]
            })
        
        cursor.execute('''
            SELECT a.id, a.start_time, a.end_time, 
                   a.annotation, a.translation, a.language,
                   a.lexical_id, a.speaker, a.addressee
            FROM annotations a
            WHERE a.language = ?
            ORDER BY a.start_time
        ''', (language,))
        
        annotations = []
        for row in cursor.fetchall():
            annotations.append({
                'id': f'annot_{row[0]}',
                'start': row[1],
                'end': row[2],
                'annotation': row[3],
                'translation': row[4],
                'language': row[5],
                'lexical_id': row[6],
                'speaker': row[7],
                'addressee': row[8]
            })
        
        conn.close()
        
        # Build EAF
        return self._build_eaf(media_files, annotations, output_path)
    
    def _build_eaf(self,
                  media_files: List[Dict],
                  annotations: List[Dict],
                  output_path: str) -> str:
        """Build EAF XML"""
        # Build media descriptors
        media_xml = ''.join(
            f'<MEDIA_DESCRIPTOR MEDIA_URL="{self._escape_xml(m["path"])}" '
            f'MIME_TYPE="video/mp4" RELATIVE_URL="true" '
            f'EXTRACT_DURATION="{m["duration"]}" '
            f'EXTRACT_FRAMES="{int(m["duration"]*25)}"/>' 
            for m in media_files
        )
        
        # Build time order
        time_order = []
        for annot in annotations:
            time_order.append(
                f'<TIME_SLOT TIME_SLOT_ID="ts{annot["id"]}_start" '
                f'TIME_VALUE="{int(annot["start"]*1000)}"/>'
            )
            time_order.append(
                f'<TIME_SLOT TIME_SLOT_ID="ts{annot["id"]}_end" '
                f'TIME_VALUE="{int(annot["end"]*1000)}"/>'
            )
        
        # Build tiers
        tiers = {}
        for annot in annotations:
            tier_id = f'tier_{annot["language"]}_{annot.get("speaker", "unknown")}'
            if tier_id not in tiers:
                tiers[tier_id] = []
            
            annotation_value = self._escape_xml(annot['annotation'])
            translation_value = self._escape_xml(annot['translation']) if annot['translation'] else ''
            
            tiers[tier_id].append(
                f'<ANNOTATION>\n'
                f'    <ALIGNABLE_ANNOTATION ANNOTATION_ID="annot_{annot["id"]}"\n'
                f'                          TIME_SLOT_REF1="ts{annot["id"]}_start"\n'
                f'                          TIME_SLOT_REF2="ts{annot["id"]}_end">\n'
                f'        <ANNOTATION_VALUE>{annotation_value}</ANNOTATION_VALUE>\n'
                f'    </ALIGNABLE_ANNOTATION>\n'
                f'    <TRANSLATION>\n'
                f'        <ANNOTATION_VALUE>{translation_value}</ANNOTATION_VALUE>\n'
                f'    </TRANSLATION>\n'
                f'</ANNOTATION>'
            )
        
        eaf_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<EAF xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xmlns:xi="http://www.w3.org/2001/XInclude"
     xmlns:fn="http://www.w3.org/2005/xpath-functions"
     xmlns:tei="http://www.tei-c.org/ns/1.0"
     xmlns="http://www.mpi.nl/elan/eaf"
     xsi:schemaLocation="http://www.mpi.nl/elan/eaf http://www.mpi.nl/elan/eaf/2.10/eaf.xsd">
    <HEADER>
        <MEDIA_DESCRIPTOR>{media_xml}</MEDIA_DESCRIPTOR>
        <LINGUISTIC_TYPE>
            <LINGUISTIC_TYPE GRAPHICAL_ATTTRIBUTES="tiers"
                             CONSTRAINTS="Time_Subdivision"
                             CONTROLLER="false"
                             CONTRIBUTES_TO="None"
                             PHONETIC="false"
                             PHONETIC_TYPE="none"
                             TEMPLATE="default"
                             VIEW_REF="default"
                             STEREOTYPE="linguist"
                             LOC="local"
                             LANG_REF="default"
                             LANG_DEF="default"
                             LANG="iso:{language}"
                             ANN="none"
                             EXTRACT="false"
                             EXTRACT_FRAMES="0"
                             EXTRACT_SAMPLES="0"
                             EXTRACT_DURATION="0"
                             LEX="false"
                             CONTROLLED="false"
                             INTERNAL_PARTITION="false"
                             HIERARCHY="Time"
                             DEFAULT="false"
                             ANNOTATION_LEVEL="None"
                             ANALYSIS_GRANULARITY="None"
                             EXTRACT_SENSITIVE="false"
                             EXTRACT_SENSITIVE_FRAMES="0"
                             EXTRACT_SENSITIVE_SAMPLES="0"
                             EXTRACT_SENSITIVE_DURATION="0"
                             ID="linguistic_type_1"
                             MIME_TYPE="text/notation"
                             LANG_DEF_REF="def"
                             LANG_DEF_REF_PATH="default"
                             LANG_DEF_REF_ID="default"
                             LANG_DEF_REF_ANNOTATION="default"
                             LANG_DEF_REF_EXAMPLE="default"
                             LANG_DEF_REF_PHONETIC="default"
                             LANG_DEF_REF_TRANSCRIPTION="default"
                             LANG_DEF_REF_TRANSLATION="default"
                             LANG_DEF_REF_WORD="default"/>
            <CONSTRAINT TYPE="Time_Subdivision" DESCRIPTION="Time can be subdivided into non-overlapping children"/>
        </LINGUISTIC_TYPE>
    </HEADER>
    <TIME_ORDER>{"".join(time_order)}</TIME_ORDER>
    <TIER DEFAULT_LOC="true" LINGUISTIC_TYPE_REF="linguistic_type_1" TIER_ID="default">
        {"".join(tiers.get('tier_default_unknown', []))}
    </TIER>
    {"".join(
        f'<TIER DEFAULT_LOC="true" LINGUISTIC_TYPE_REF="linguistic_type_1" TIER_ID="{tier_id}">' +
        "".join(annotations) +
        f'</TIER>'
        for tier_id, annotations in tiers.items() if tier_id != 'tier_default_unknown'
    )}
</EAF>'''
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(eaf_xml, encoding='utf-8')
        
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
        description='Export OLAC data to TMX/EAF/FLEX formats'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Harvest command
    harvest_parser = subparsers.add_parser('harvest', help='Harvest OLAC records')
    harvest_parser.add_argument('--db', default='olac_data.db', help='Database file')
    harvest_parser.add_argument('--max', type=int, default=100, help='Max records')
    harvest_parser.add_argument('--languages', nargs='+', 
                               default=['esx', 'kic', 'oka', 'mjx'],
                               help='Language codes to harvest')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract linguistic data')
    extract_parser.add_argument('--db', default='olac_data.db', help='Database file')
    
    # Export TMX command
    tmx_parser = subparsers.add_parser('export-tmx', help='Export to TMX')
    tmx_parser.add_argument('--db', default='olac_data.db', help='Database file')
    tmx_parser.add_argument('--output', required=True, help='Output TMX file')
    tmx_parser.add_argument('--source', required=True, help='Source language')
    tmx_parser.add_argument('--target', required=True, help='Target language')
    
    # Export EAF command
    eaf_parser = subparsers.add_parser('export-eaf', help='Export to EAF')
    eaf_parser.add_argument('--db', default='olac_data.db', help='Database file')
    eaf_parser.add_argument('--output', required=True, help='Output EAF file')
    eaf_parser.add_argument('--language', default='esx', help='Language code')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.error('No command specified. Use --help to see options.')
    
    exporter = OLACExporter(db_path=args.db)
    
    if args.command == 'harvest':
        records = exporter.harvest_olac(max_records=args.max, 
                                       languages=args.languages)
        exporter.save_to_database(records)
    
    elif args.command == 'extract':
        exporter.extract_linguistic_data()
    
    elif args.command == 'export-tmx':
        exporter.export_tmx(
            output_path=args.output,
            source_lang=args.source,
            target_lang=args.target
        )
    
    elif args.command == 'export-eaf':
        exporter.export_eaf(
            output_path=args.output,
            language=args.language
        )

if __name__ == '__main__':
    import time
    main()
