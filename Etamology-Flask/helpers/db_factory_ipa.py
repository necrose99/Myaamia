# helpers/db_factory_ipa.py
"""
Lightweight IPA & Phonetic DB Manager for Algic / Myaamia.
Handles TMX parsing, deterministic G2P transliteration, and lightweight SQLite storage.
"""

import sqlite3
import lxml.etree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional
from helpers.db_factory import db_sql

# Cultural voice rules
GENDER_RULES = {
    "iihia": "male",
    "iiia": "male",
    "naaka": "female"
}

# Algic/Myaamia orthography-to-IPA mapping (Deterministic fallback)
ORTHO_TO_IPA_RULES = [
    ('Å¡', 'š'),
    ('aa', 'aː'), ('ee', 'ɛː'), ('ii', 'iː'), ('oo', 'oː'),
    ('ay', 'aj'), ('aw', 'aw'),
    ('hk', 'ʰk'), ('ht', 'ʰt'), ('hp', 'ʰp'), ('hc', 'ʰtʃ'),
    ('š', 'ʃ'),  ('č', 'tʃ'), ('c', 'tʃ')
]

# Web Speech API phonetic hint mapping for fallback TTS
IPA_TO_WEB_TTS = {
    "aː": "aa", "ɛː": "eh", "iː": "ee", "oː": "oh",
    "aj": "eye", "aw": "ow",
    "ʰk": "hk", "ʰt": "ht", "ʰp": "hp", "ʰtʃ": "h-ch",
    "ʃ": "sh", "tʃ": "ch"
}


class IPAMapping(db_sql.Model):
    """SQLAlchemy model for IPA and TTS lookup."""
    __tablename__ = 'ipa_mappings'

    id = db_sql.Column(db_sql.Integer, primary_key=True)
    word = db_sql.Column(db_sql.String(150), unique=True, nullable=False, index=True)
    lang = db_sql.Column(db_sql.String(10), default='mia')
    ipa = db_sql.Column(db_sql.String(150))
    tts_hint = db_sql.Column(db_sql.String(150))
    voice_profile = db_sql.Column(db_sql.String(20), default='neutral')
    audio_url = db_sql.Column(db_sql.String(255), nullable=True)


class IPATTSManager:
    """Slim database helper for IPA and TTS operations."""

    @staticmethod
    def myaamia_to_ipa(text: str) -> str:
        """Best-guess G2P transliteration for Myaamia/Algic terms."""
        if not text:
            return ""
        ipa = text.lower().strip('-')
        for orth, phon in ORTHO_TO_IPA_RULES:
            ipa = ipa.replace(orth, phon)
        return f"/{ipa}/"

    @staticmethod
    def ipa_to_tts_hint(ipa_str: str) -> str:
        """Translates IPA string to Web Speech API printable phonetic hint."""
        clean = ipa_str.strip('/')
        for ipa, approx in IPA_TO_WEB_TTS.items():
            clean = clean.replace(ipa, approx)
        return clean

    @staticmethod
    def get_voice_profile(word: str) -> str:
        clean = word.lower().strip('-')
        return GENDER_RULES.get(clean, "neutral")

    @classmethod
    def enrich_and_store_tmx(cls, db_path: str, tmx_file: str):
        """Enriches SQLite store with terms parsed from TMX files."""
        if not Path(tmx_file).exists():
            return

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        tree = ET.parse(tmx_file)
        for tu in tree.xpath("//tu"):
            tuv_seg = tu.xpath(".//tuv[@xml:lang='mia']/seg")
            if not tuv_seg or not tuv_seg[0].text:
                continue

            word_raw = tuv_seg[0].text
            word_clean = word_raw.replace('Å¡', 'š')
            ipa_val = cls.myaamia_to_ipa(word_clean)
            tts_hint = cls.ipa_to_tts_hint(ipa_val)
            voice = cls.get_voice_profile(word_clean)

            cur.execute("""
                INSERT INTO ipa_mappings (word, lang, ipa, tts_hint, voice_profile)
                VALUES (?, 'mia', ?, ?, ?)
                ON CONFLICT(word) DO UPDATE SET
                    ipa = excluded.ipa,
                    tts_hint = excluded.tts_hint,
                    voice_profile = excluded.voice_profile
            """, (word_clean, ipa_val, tts_hint, voice))

        conn.commit()
        conn.close()

    @classmethod
    def export_manifest(cls, db_path: str) -> Dict[str, Any]:
        """Generates a lean dict manifest consumed directly by static JS."""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        manifest = {}
        cur.execute("SELECT word, lang, ipa, tts_hint, voice_profile, audio_url FROM ipa_mappings")
        for row in cur.fetchall():
            key = row['word'].strip('-').lower()
            manifest[key] = {
                "orthography": row['word'],
                "lang": row['lang'],
                "ipa": row['ipa'] or "",
                "tts_hint": row['tts_hint'] or "",
                "voice": row['voice_profile'] or "neutral",
                "audio_url": row['audio_url'] or "",
                "has_recording": bool(row['audio_url'])
            }

        conn.close()
        return manifest
        # helpers/db_factory_ipa.py
import sqlite3
import lxml.etree as ET
from pathlib import Path

def init_ipa_schema(conn: sqlite3.Connection):
    """Ensures IPA and lexical schema exist in the database."""
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS lexical_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE NOT NULL,
            language_code TEXT DEFAULT 'mia',
            ipa TEXT,
            ilda_id TEXT,
            voice_gender TEXT DEFAULT 'neutral',
            audio_url TEXT
        )
    ''')
    existing_cols = [row[1] for row in cur.execute("PRAGMA table_info(lexical_items)").fetchall()]
    for col in ["ipa", "ilda_id", "voice_gender", "audio_url"]:
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE lexical_items ADD COLUMN {col} TEXT")
    conn.commit()

def sync_tmx_to_db(conn: sqlite3.Connection, tmx_path: str, g2p_func, voice_profile_func):
    """Parses TMX and updates lexical entries."""
    if not Path(tmx_path).exists():
        return False, f"TMX file not found: {tmx_path}"

    init_ipa_schema(conn)
    cur = conn.cursor()
    tree = ET.parse(tmx_path)
    count = 0

    for tu in tree.xpath("//tu"):
        ilda_id = tu.findtext(".//prop[@type='x-ilda-id']")
        tuv_seg = tu.xpath(".//tuv[@xml:lang='mia']/seg")
        if not tuv_seg or not tuv_seg[0].text:
            continue

        myaamia_clean = tuv_seg[0].text.replace('Å¡', 'š')
        ipa_val = g2p_func(myaamia_clean)
        voice = voice_profile_func(myaamia_clean)

        cur.execute('''
            INSERT INTO lexical_items (word, language_code, ipa, ilda_id, voice_gender)
            VALUES (?, 'mia', ?, ?, ?)
            ON CONFLICT(word) DO UPDATE SET
                ipa = excluded.ipa,
                ilda_id = excluded.ilda_id,
                voice_gender = excluded.voice_gender
        ''', (myaamia_clean, ipa_val, ilda_id, voice))
        count += 1

    conn.commit()
    return True, f"Enriched {count} entries from TMX."