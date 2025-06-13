-- Main Entries Table
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY,
    myaamia_word TEXT NOT NULL,
    english_definition TEXT,
    french_definition TEXT,
    part_of_speech TEXT,
    root_form TEXT,
    ipa TEXT
);

-- RAGLite Embeddings Table
CREATE VIRTUAL TABLE IF NOT EXISTS embeddings USING vec0(
    document TEXT PRIMARY KEY,
    embedding FLOAT[1024]
);

-- Affix Rules Table
CREATE TABLE IF NOT EXISTS affix_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    affix TEXT NOT NULL,
    description TEXT
);

-- Translation Memory (TMX) Table
CREATE TABLE IF NOT EXISTS translation_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_text TEXT NOT NULL,
    target_text TEXT NOT NULL,
    source_lang TEXT NOT NULL,
    target_lang TEXT NOT NULL
);

-- OML Metadata Table
CREATE TABLE IF NOT EXISTS oml_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    version TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
