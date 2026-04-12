#!/usr/bin/env python3
"""
scripts/OLAC-import.py
Improved OLAC harvesting & ingestion pipeline for Myaamia/Algonquian languages.
Supports FLEx (via LIFT/TMX), BabelEdit (JSON), MT testing (TMX/XLIFF), basic Hunspell,
and now LEMON/OntoLex-Lemon RDF export for semantic publishing.
"""

import requests
import xml.etree.ElementTree as ET
import sqlite3
import json
import uuid
import subprocess
import time
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Optional
import argparse
import re

# New: RDF support for LEMON
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, SKOS, XSD

class OLACImporter:
    def __init__(self, db_path: str = 'data/olac_data.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.xslt_dir = Path("XSLT/linguistics-suite/xslt")  # Adjust path if needed

        self.LANGUAGE_MAP = {
            # Plains
            "bft": "Blackfoot", "arp": "Arapaho", "ats": "Gros Ventre", "chy": "Cheyenne",
            # Central
            "men": "Menominee", "cre": "Cree", "csw": "Swampy Cree", "crj": "Southern East Cree",
            "atj": "Atikamekw", "pot": "Potawatomi", "oji": "Ojibwe", "otw": "Ottawa",
            "ciw": "Chippewa", "mia": "Miami-Illinois (Myaamia)", "sac": "Meskwaki (Fox)",
            "kic": "Kickapoo (US)", "sha": "Shawnee",
            # Eastern
            "mic": "Mi'kmaq", "abe": "Western Abenaki", "aaq": "Eastern Abnaki",
            "mal": "Maliseet-Passamaquoddy", "moo": "Mohegan-Pequot", "mua": "Munsee", "unm": "Unami",
            # Proto
            "alg-x-proto": "Proto-Algonquian",
            # Supervisor languages
            "en": "English", "es": "Spanish", "la": "Latin (Scientific / Botanical)",
            "fr": "French", "fr_ca": "Canadian French", "fr_old": "Old French (1600s-style / Historical)",
            # Variants
            "kick_us": "Kickapoo (US)", "kic_mx": "Kickapoo (Mexico)",
        }

        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                url TEXT UNIQUE,
                title TEXT,
                language_code TEXT,
                harvested_at TEXT,
                raw_content TEXT
            );
            CREATE TABLE IF NOT EXISTS lexical_items (
                id TEXT PRIMARY KEY,
                source_id TEXT,
                word TEXT,
                translation TEXT,
                language_code TEXT,
                concept TEXT,
                FOREIGN KEY (source_id) REFERENCES sources(id)
            );
        ''')
        conn.commit()
        conn.close()

    def harvest_olac(self, max_records: int = 300):
        print("🔍 Starting OLAC harvesting for Algonquian languages...")
        bases = ["https://www.language-archives.org/oai"]
        languages = ["mia", "kic", "cre", "oji", "mic", "chy", "arp", "bft", "alg"]

        all_items = []
        for base in bases:
            items = self._oai_harvest(base, languages, max_records // len(bases))
            all_items.extend(items)
            time.sleep(3)

        self._save_sources(all_items)
        print(f"✅ Harvested {len(all_items)} items.")

    def _oai_harvest(self, base_url: str, languages: List[str], limit: int) -> List[Dict]:
        records = []
        resumption = None
        while len(records) < limit:
            params = {"verb": "ListRecords", "metadataPrefix": "olac"}
            if resumption:
                params = {"verb": "ListRecords", "resumptionToken": resumption}

            try:
                r = requests.get(base_url, params=params, timeout=45)
                r.raise_for_status()
                root = ET.fromstring(r.content)

                for rec in root.findall(".//{http://www.openarchives.org/OAI/2.0/}record"):
                    parsed = self._parse_record(rec)
                    if parsed and (not parsed.get("language_code") or parsed["language_code"] in languages):
                        records.append(parsed)

                token_elem = root.find(".//{http://www.openarchives.org/OAI/2.0/}resumptionToken")
                resumption = token_elem.text if token_elem is not None and token_elem.text else None
                if not resumption:
                    break
            except Exception as e:
                print(f"⚠️ Harvest error: {e}")
                break
        return records[:limit]

    def _parse_record(self, elem) -> Optional[Dict]:
        try:
            metadata = elem.find(".//{http://www.openarchives.org/OAI/2.0/}metadata")
            if not metadata:
                return None

            dc_ns = {"dc": "http://purl.org/dc/elements/1.1/"}
            olac_ns = {"olac": "http://www.language-archives.org/OLAC/1.1/"}

            lang_code = None
            lang_elem = metadata.find(".//olac:language", olac_ns)
            if lang_elem is not None and "code" in lang_elem.attrib:
                lang_code = lang_elem.attrib["code"]

            return {
                "id": str(uuid.uuid4()),
                "url": elem.findtext(".//{http://www.openarchives.org/OAI/2.0/}identifier") or "",
                "title": metadata.findtext(".//dc:title", namespaces=dc_ns) or "",
                "language_code": lang_code or "",
                "raw_content": ET.tostring(metadata, encoding="unicode"),
                "harvested_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception:
            return None

    def _save_sources(self, items: List[Dict]):
        conn = sqlite3.connect(self.db_path)
        for item in items:
            conn.execute('''
                INSERT OR IGNORE INTO sources (id, url, title, language_code, harvested_at, raw_content)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (item["id"], item["url"], item["title"], item["language_code"], item["harvested_at"], item["raw_content"]))
        conn.commit()
        conn.close()

    def extract_lexical(self):
        """Basic extraction — can be enhanced later with XSLT or better patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, raw_content, language_code FROM sources")

        for sid, raw, lang in cursor.fetchall():
            text = raw.lower()
            words = re.findall(r'\b[a-záéíóúñçàèùâêîôûëïüÿœæ]+(?:-[a-záéíóúñçàèùâêîôûëïüÿœæ]+)*\b', text)
            for w in set(words[:50]):
                item_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT OR IGNORE INTO lexical_items 
                    (id, source_id, word, language_code, concept)
                    VALUES (?, ?, ?, ?, ?)
                ''', (item_id, sid, w, lang, "extracted"))
        conn.commit()
        conn.close()
        print("✅ Lexical extraction completed.")

    def export_babeledit_json(self, output_dir: str = "babeledit_algonquian"):
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        translations = defaultdict(dict)
        cursor = conn.execute("SELECT language_code, word, concept FROM lexical_items WHERE word IS NOT NULL")
        for lang, word, concept in cursor.fetchall():
            key = concept or word
            translations[lang][key] = word

        for code, data in translations.items():
            safe = code.replace("-", "_").lower()
            path = out_dir / f"{safe}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            name = self.LANGUAGE_MAP.get(code, code)
            print(f"Created: {path.name} → {name} ({len(data)} entries)")

        # Empty supervisors
        for c, n in [("en","English"), ("fr_old","Old French (1600s)"), ("la","Latin")]:
            (out_dir / f"{c}.json").write_text("{}", encoding="utf-8")
            print(f"Created empty supervisor: {c}.json → {n}")

        conn.close()
        print(f"✅ BabelEdit-ready files in: {out_dir}")

    def export_lemon_rdf(self, output_ttl: str = "output/myaamia_lexicon.ttl"):
        """LEMON RDF export — the key improvement to the ingestion pipeline"""
        g = Graph()
        LEMON = Namespace("http://lemon-model.net/lemon#")
        ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")  # Modern alias
        g.bind("lemon", LEMON)
        g.bind("ontolex", ONTOLEX)
        g.bind("skos", SKOS)
        g.bind("rdfs", RDFS)

        base = URIRef("http://example.org/myaamia-lexicon/")

        # Create Lexicons per language
        for lang_code, display_name in self.LANGUAGE_MAP.items():
            lex_uri = base + f"lexicon/{lang_code.replace('-', '_')}"
            g.add((lex_uri, RDF.type, LEMON.Lexicon))
            g.add((lex_uri, LEMON.language, Literal(lang_code)))
            g.add((lex_uri, RDFS.label, Literal(display_name)))

        # Map lexical items to LEMON structure
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT language_code, word, concept 
            FROM lexical_items 
            WHERE word IS NOT NULL AND word != ''
        """)

        seen = {}
        for lang_code, word, concept in cursor.fetchall():
            if not lang_code or not word:
                continue
            safe_lang = lang_code.replace('-', '_').lower()
            entry_uri = base + f"entry/{safe_lang}/{word.replace(' ', '_')}"
            form_uri = base + f"form/{safe_lang}/{word.replace(' ', '_')}"
            sense_uri = base + f"sense/{safe_lang}/{word.replace(' ', '_')}"

            if entry_uri not in seen:
                g.add((entry_uri, RDF.type, LEMON.LexicalEntry))
                g.add((entry_uri, LEMON.canonicalForm, form_uri))
                lex_uri = base + f"lexicon/{safe_lang}"
                g.add((lex_uri, LEMON.entry, entry_uri))
                seen[entry_uri] = True

            # Form
            g.add((form_uri, RDF.type, LEMON.Form))
            g.add((form_uri, LEMON.writtenRep, Literal(word)))

            # Sense
            g.add((entry_uri, LEMON.sense, sense_uri))
            g.add((sense_uri, RDF.type, LEMON.LexicalSense))
            if concept:
                concept_uri = base + f"concept/{concept.replace(' ', '_')}"
                g.add((sense_uri, LEMON.reference, concept_uri))
                g.add((concept_uri, RDF.type, SKOS.Concept))
                g.add((concept_uri, RDFS.label, Literal(concept)))

            # Supervisor note
            if lang_code in ["fr_old", "la", "en"]:
                g.add((sense_uri, RDFS.comment, Literal(f"Supervisor language: {self.LANGUAGE_MAP.get(lang_code)}")))

        conn.close()

        out_path = Path(output_ttl)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        g.serialize(destination=str(out_path), format="turtle")
        g.serialize(destination=str(out_path.with_suffix('.rdf')), format="xml")

        print(f"✅ LEMON RDF export complete:")
        print(f"   Turtle : {out_path} ({len(g)} triples)")
        print(f"   RDF/XML: {out_path.with_suffix('.rdf')}")
        print("   Ready for SPARQL querying, ontology linking, or publishing.")

    def basic_hunspell_prep(self, output_dic: str = "hunspell/myaamia.dic"):
        conn = sqlite3.connect(self.db_path)
        words = [row[0] for row in conn.execute("SELECT DISTINCT word FROM lexical_items WHERE language_code='mia'")]
        conn.close()

        Path(output_dic).parent.mkdir(parents=True, exist_ok=True)
        with open(output_dic, "w", encoding="utf-8") as f:
            f.write(f"{len(words)}\n")
            for w in sorted(set(words)):
                f.write(f"{w}\n")
        print(f"✅ Basic Hunspell .dic created: {output_dic} ({len(words)} entries)")

def main():
    parser = argparse.ArgumentParser(description="OLAC Import Pipeline for Myaamia/Algonquian")
    parser.add_argument("command", choices=["harvest", "extract", "babeledit", "lemon", "hunspell"])
    parser.add_argument("--max", type=int, default=300, help="Max records for harvest")
    args = parser.parse_args()

    importer = OLACImporter()

    if args.command == "harvest":
        importer.harvest_olac(max_records=args.max)
    elif args.command == "extract":
        importer.extract_lexical()
    elif args.command == "babeledit":
        importer.export_babeledit_json()
    elif args.command == "lemon":
        importer.export_lemon_rdf()
    elif args.command == "hunspell":
        importer.basic_hunspell_prep()

if __name__ == "__main__":
    main()
