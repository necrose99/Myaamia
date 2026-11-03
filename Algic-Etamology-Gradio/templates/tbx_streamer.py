"""
tbx_streamer.py
Streams TBX XML data, generates fro/fr lookup indices, and populates the database.
"""

import xml.etree.ElementTree as ET
import sqlite3
import os
from whoosh.index import open_dir
from transformers import pipeline

class TBXNormalizationStreamer:
    def __init__(self, db_path="sparql_cache.db", index_dir="whoosh_index"):
        self.db_path = db_path
        self.index_dir = index_dir
        
        # Load the Hugging Face Old French to Modern French transformation layer
        print("Loading Hugging Face 'fro-fr-normalizer' engine...")
        self.fro_normalizer = pipeline(
            "text2text-generation", 
            model="bramvanroy/fro-fr-normalizer"
        )
        self._init_db()

    def _init_db(self):
        """Initializes the relational mapping database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tbx_lexicon (
                term_id TEXT PRIMARY KEY,
                english_key TEXT,
                modern_french TEXT,
                old_french_lookup TEXT,
                notes TEXT
            );
        """)
        # Index keys for lightning-fast cross-referencing and tool hover lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_en_key ON tbx_lexicon(english_key);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fro_lookup ON tbx_lexicon(old_french_lookup);")
        conn.commit()
        conn.close()

    def stream_and_index_tbx(self, tbx_file_path):
        """
        Streams TBX entry structures natively, normalizes French data, 
        and updates relational SQL entries and Whoosh full-text indices.
        """
        if not os.path.exists(tbx_file_path):
            print(f"File not found: {tbx_file_path}")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Open Whoosh Index Writer if the index directory exists
        whoosh_writer = None
        if os.path.exists(self.index_dir):
            ix = open_dir(self.index_dir)
            whoosh_writer = ix.writer()

        print(f"Streaming and processing terminological entries from {tbx_file_path}...")
        
        # Use incremental streaming parsing to stay memory-safe
        context = ET.iterparse(tbx_file_path, events=("end",))
        
        for event, elem in context:
            # Match standard TBX termEntry structural elements
            if elem.tag == "termEntry":
                term_id = elem.get("id", "unknown_id")
                english_term = ""
                modern_french_term = ""
                notes = ""

                # Navigate inner langSet structures
                for lang_set in elem.findall("langSet"):
                    lang = lang_set.get("{http://w3.org}lang")
                    
                    if lang == "en":
                        term_elem = lang_set.find(".//term")
                        if term_elem is not None:
                            english_term = term_elem.text
                            
                    elif lang == "fr":
                        term_elem = lang_set.find(".//term")
                        if term_elem is not None:
                            modern_french_term = term_elem.text
                            
                    # Optional: Grab descriptive notes or historical usage examples
                    note_elem = lang_set.find(".//note")
                    if note_elem is not None:
                        notes = note_elem.text

                if english_term and modern_french_term:
                    # Generate the Old French (fro) reverse-lookup variant via the model
                    # This maps out archaic variant spellings for your search parameters
                    generation = self.fro_normalizer(
                        f"moderniser: {modern_french_term}", # Prompt framing depends on specific model tuning
                        max_length=128
                    )
                    old_french_variant = generation[0]['generated_text']

                    # 1. Write straight to SQL Database Cache
                    cursor.execute("""
                        INSERT OR REPLACE INTO tbx_lexicon 
                        (term_id, english_key, modern_french, old_french_lookup, notes)
                        VALUES (?, ?, ?, ?, ?);
                    """, (term_id, english_term, modern_french_term, old_french_variant, notes))

                    # 2. Sync to Whoosh full-text index for real-time autocompletion
                    if whoosh_writer:
                        searchable_blob = f"EN: {english_term} | FR: {modern_french_term} | FRO: {old_french_variant} | {notes}"
                        whoosh_writer.update_document(
                            id=term_id,
                            title=f"{english_term} / {modern_french_term}",
                            body=searchable_blob
                        )
                        
                    print(f"Processed: [EN]: {english_term} ➔ [FR]: {modern_french_term} (Lookup Variant [FRO]: {old_french_variant})")

                # Clean up memory references for processed elements
                elem.clear()
                
        conn.commit()
        conn.close()
        
        if whoosh_writer:
            whoosh_writer.commit()
        print("✓ TBX stream ingestion and index compilation successfully finished.")

# --- Generate Mock TBX File for Testing ---
def generate_sample_tbx():
    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <martif type="TBX" xml:lang="en">
        <text>
            <body>
                <termEntry id="term_001">
                    <langSet xml:lang="en"><term>blood</term></langSet>
                    <langSet xml:lang="fr"><term>sang</term><note>Historical variant orthographies include ashaboouth.</note></langSet>
                </termEntry>
                <termEntry id="term_002">
                    <langSet xml:lang="en"><term>water</term></langSet>
                    <langSet xml:lang="fr"><term>eau</term></langSet>
			<langSet xml:lang="mia"><term>nipi</term></langSet>
			<langSet xml:lang="sjw"><term>nepi</term></langSet>

                </termEntry>
            </body>
        </text>
    </martif>
    """
    with open("sample_import.tbx", "w", encoding="utf-8") as f:
        f.write(sample_xml)

if __name__ == "__main__":
    generate_sample_tbx()
    streamer = TBXNormalizationStreamer()
    streamer.stream_and_index_tbx("sample_import.tbx")