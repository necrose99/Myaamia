13_exports_base-rag-sqlite.sql
-- Output export tables and views for TMX, GPT, HuggingFace JSONL etc.
CREATE TABLE IF NOT EXISTS translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_lang TEXT NOT NULL,
    target_lang TEXT NOT NULL,
    source_text TEXT NOT NULL,
    target_text TEXT NOT NULL,
    context TEXT,
    source_reference TEXT,
    confidence_score REAL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
