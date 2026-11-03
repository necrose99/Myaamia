# helpers/db_factory_audio.py
import sqlite3

def update_audio_mapping(conn: sqlite3.Connection, word: str, audio_url: str):
    """Links a static MP3 audio path to a word entry."""
    cur = conn.cursor()
    cur.execute('''
        UPDATE lexical_items 
        SET audio_url = ? 
        WHERE LOWER(TRIM(word, '-')) = LOWER(TRIM(?, '-'))
    ''', (audio_url, word))
    conn.commit()

def fetch_all_lexical_rows(conn: sqlite3.Connection):
    """Retrieves all lexical records for speech manifest/API output."""
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, word, language_code, ipa, ilda_id, voice_gender, audio_url FROM lexical_items")
    return cur.fetchall()