--13_exports_base-rag-sqlite.sql
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
-- =======================
-- CLAUDE.AI METADATA
-- =======================

-- Claude.ai Processing Metadata
CREATE TABLE IF NOT EXISTS claude_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Model information
    model_name TEXT NOT NULL DEFAULT 'claude-sonnet-4',
    model_version TEXT,
    api_version TEXT,
    
    -- Processing session
    session_id TEXT,
    processing_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Task metadata
    task_type TEXT, -- 'entry_generation', 'etymology_analysis', 'translation', etc.
    input_data TEXT, -- JSON of input parameters
    output_data TEXT, -- JSON of results
    
    -- Quality metrics
    confidence_score REAL,
    processing_time_ms INTEGER,
    token_count INTEGER,
    
    -- Validation
    human_reviewed BOOLEAN DEFAULT FALSE,
    validation_status TEXT CHECK (validation_status IN ('pending', 'approved', 'rejected', 'needs_revision')),
    reviewer_notes TEXT,
    
    -- Links to affected records
    affected_tables TEXT, -- JSON array of table names
    affected_ids TEXT -- JSON array of record IDs
);

-- OML (Open Model Library) Metadata for Public Publishing
CREATE TABLE IF NOT EXISTS oml_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Model identification
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    model_type TEXT CHECK (model_type IN ('language_model', 'translation_model', 'embedding_model', 'classification_model')),
    
    -- Miami-Illinois specific
    training_data_size INTEGER, -- Number of Miami-Illinois examples
    vocabulary_size INTEGER,
    coverage_percentage REAL, -- Percentage of Miami-Illinois vocabulary covered
    
    -- Model metadata
    architecture TEXT, -- transformer, lstm, etc.
    parameter_count BIGINT,
    training_steps INTEGER,
    training_duration_hours REAL,
    
    -- Performance metrics
    bleu_score REAL, -- For translation models
    perplexity REAL, -- For language models
    accuracy REAL, -- For classification
    f1_score REAL,
    
    -- Dataset information
    training_dataset_id TEXT,
    validation_dataset_id TEXT,
    test_dataset_id TEXT,
    
    -- Licensing and publication
    license TEXT DEFAULT 'CC-BY-SA-4.0',
    is_public BOOLEAN DEFAULT FALSE,
    huggingface_repo TEXT, -- Repository name on HF
    model_card_url TEXT,
    
    -- Technical details
    required_libraries TEXT, -- JSON array
    inference_framework TEXT, -- pytorch, tensorflow, onnx
    quantization_type TEXT, -- int8, int4, fp16, etc.
    
    -- Collaboration
    contributors TEXT, -- JSON array of contributor names
    acknowledgments TEXT,
    funding_sources TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP
);
