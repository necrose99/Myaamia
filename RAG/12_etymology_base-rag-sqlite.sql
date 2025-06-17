--12_etymology_base-rag-sqlite.sql
-- WikiLang Compliant Miami-Illinois Language Database Schema
-- ISO 639-3: mia, Glottolog: miam1252
-- Supports RAGLite embeddings and Claude.ai metadata

-- =======================
-- CORE LANGUAGE TABLES
-- =======================

-- Main Lexical Entries Table (WikiLang compliant)
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Core entry data
    headword TEXT NOT NULL, -- Main Miami-Illinois form
    normalized_form TEXT, -- Standardized orthography
    pos TEXT, -- Part of speech (noun, verb, particle, etc.)
    
    -- Definitions in related languages
    english_definition TEXT,
    french_definition TEXT, -- Historical French sources
    sauk_definition TEXT, -- ISO: sac, related Algonquian
    kickapoo_definition TEXT, -- ISO: kic, Glottolog: kick1244
    potawatomi_definition TEXT, -- ISO: pot, Glottolog: pota1247
    
    -- Linguistic data
    ipa_transcription TEXT, -- IPA pronunciation
    stress_pattern TEXT, -- Stress marking
    syllable_count INTEGER,
    
    -- Morphological data
    root_form TEXT,
    stem_class TEXT, -- Animate/inanimate, verb class, etc.
    inflection_class TEXT,
    
    -- Metadata
    frequency_rank INTEGER,
    attestation_level TEXT CHECK (attestation_level IN ('well-attested', 'limited', 'reconstructed', 'unverified')),
    semantic_domain TEXT, -- Cultural/semantic category
    register TEXT, -- Formal, colloquial, ceremonial, etc.
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- WikiLang compliance
    wikidata_id TEXT, -- Q-number if available
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'deprecated', 'variant'))
);

-- =======================
-- ETYMOLOGY TABLES
-- =======================

-- Etymology Sources and Reconstructions
CREATE TABLE IF NOT EXISTS etymologies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    
    -- Proto-form data
    proto_form TEXT, -- Proto-Algonquian reconstruction
    proto_language TEXT, -- PA, PAC, etc.
    reconstruction_confidence TEXT CHECK (reconstruction_confidence IN ('certain', 'probable', 'possible', 'speculative')),
    
    -- Historical development
    sound_changes TEXT, -- Documented sound changes
    semantic_development TEXT, -- Meaning changes over time
    
    -- Cognates in related languages
    ojibwe_cognate TEXT,
    ottawa_cognate TEXT,
    cree_cognate TEXT,
    menominee_cognate TEXT,
    
    -- Sources
    etymology_source_id INTEGER,
    notes TEXT,
    
    FOREIGN KEY (entry_id) REFERENCES entries(id),
    FOREIGN KEY (etymology_source_id) REFERENCES sources(id)
);

-- Derivational Morphology
CREATE TABLE IF NOT EXISTS derivations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    derived_entry_id INTEGER NOT NULL,
    base_entry_id INTEGER,
    
    -- Derivation process
    derivation_type TEXT, -- prefixation, suffixation, compounding, etc.
    affix_used TEXT,
    semantic_change TEXT,
    productivity TEXT CHECK (productivity IN ('productive', 'semi-productive', 'lexicalized')),
    
    -- Historical notes
    historical_notes TEXT,
    
    FOREIGN KEY (derived_entry_id) REFERENCES entries(id),
    FOREIGN KEY (base_entry_id) REFERENCES entries(id)
);
