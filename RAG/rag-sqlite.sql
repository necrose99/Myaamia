-- =======================
-- PHONOLOGY TABLES
-- =======================

-- Phoneme Inventory
CREATE TABLE IF NOT EXISTS phonemes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Phoneme representation
    ipa_symbol TEXT NOT NULL UNIQUE,
    native_orthography TEXT, -- How written in Miami-Illinois
    phoneme_type TEXT CHECK (phoneme_type IN ('vowel', 'consonant', 'tone', 'stress')),
    
    -- Articulatory features (for consonants)
    manner TEXT, -- stop, fricative, nasal, etc.
    place TEXT, -- bilabial, alveolar, etc.
    voicing TEXT CHECK (voicing IN ('voiced', 'voiceless', 'n/a')),
    
    -- Vowel features
    height TEXT, -- high, mid, low
    backness TEXT, -- front, central, back
    roundness TEXT CHECK (roundness IN ('rounded', 'unrounded', 'n/a')),
    length TEXT CHECK (length IN ('short', 'long', 'n/a')),
    
    -- Phonological status
    phonemic_status TEXT CHECK (phonemic_status IN ('phoneme', 'allophone', 'marginal')),
    frequency TEXT CHECK (frequency IN ('common', 'uncommon', 'rare')),
    
    -- Notes
    allophone_description TEXT,
    distribution_notes TEXT,
    historical_development TEXT
);

-- Phonological Processes
CREATE TABLE IF NOT EXISTS phonological_processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Process description
    process_name TEXT NOT NULL,
    process_type TEXT, -- assimilation, deletion, insertion, etc.
    input_context TEXT, -- Phonological environment
    output_result TEXT,
    
    -- Conditions
    morphological_context TEXT, -- Where it applies
    lexical_exceptions TEXT,
    obligatory BOOLEAN DEFAULT TRUE,
    
    -- Examples
    example_input TEXT,
    example_output TEXT,
    
    -- Documentation
    source_id INTEGER,
    notes TEXT,
    
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- Syllable Structure
CREATE TABLE IF NOT EXISTS syllable_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    
    -- Syllable breakdown
    syllable_structure TEXT, -- CV, CVC, etc.
    syllable_boundaries TEXT, -- With dots or hyphens
    stress_assignment TEXT,
    
    -- Phonotactic constraints
    onset_clusters TEXT,
    coda_restrictions TEXT,
    
    FOREIGN KEY (entry_id) REFERENCES entries(id)
);



-- Entry-Source Links (many-to-many)
CREATE TABLE IF NOT EXISTS entry_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    
    -- Specific citation info
    page_reference TEXT,
    confidence_level TEXT CHECK (confidence_level IN ('certain', 'probable', 'questionable')),
    notes TEXT,
    
    FOREIGN KEY (entry_id) REFERENCES entries(id),
    FOREIGN KEY (source_id) REFERENCES sources(id),
    UNIQUE(entry_id, source_id)
);

-- =======================
-- MORPHOLOGY TABLES
-- =======================

-- Affix and Morpheme Inventory
CREATE TABLE IF NOT EXISTS morphemes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Morpheme form
    morpheme_form TEXT NOT NULL,
    allomorphs TEXT, -- JSON array of variant forms
    morpheme_type TEXT CHECK (morpheme_type IN ('root', 'prefix', 'suffix', 'infix', 'circumfix', 'clitic')),
    
    -- Semantic/grammatical function
    grammatical_function TEXT,
    semantic_meaning TEXT,
    
    -- Morphological properties
    productivity TEXT CHECK (productivity IN ('productive', 'semi-productive', 'lexicalized')),
    selectional_restrictions TEXT,
    ordering_constraints TEXT,
    
    -- Phonological effects
    phonological_changes TEXT, -- Changes it causes to stem
    stress_effects TEXT,
    
    -- Historical data
    etymology TEXT,
    cognates TEXT,
    
    -- Examples
    example_forms TEXT -- JSON array of examples
);

-- Inflectional Paradigms
CREATE TABLE IF NOT EXISTS inflection_paradigms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paradigm_name TEXT NOT NULL,
    pos TEXT NOT NULL,
    
    -- Paradigm structure
    dimensions TEXT, -- JSON: person, number, tense, etc.
    paradigm_data TEXT, -- JSON: complete paradigm table
    
    -- Morphophonological notes
    stem_changes TEXT,
    irregular_forms TEXT,
    
    -- Usage notes
    frequency TEXT,
    register_restrictions TEXT,
    
    -- Documentation
    source_id INTEGER,
    examples TEXT, -- JSON array
    
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- =======================
-- RAGLITE INTEGRATION
-- =======================

-- RAGLite Vector Embeddings
CREATE VIRTUAL TABLE IF NOT EXISTS embeddings USING vec0(
    document_id TEXT PRIMARY KEY,
    embedding FLOAT[1024],
    document_type TEXT, -- 'entry', 'etymology', 'example', etc.
    content_hash TEXT,
    metadata TEXT -- JSON metadata
);

-- Document Chunks for RAG
CREATE TABLE IF NOT EXISTS document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Document reference
    source_table TEXT NOT NULL, -- Which table the content comes from
    source_id INTEGER NOT NULL, -- ID in that table
    
    -- Chunk data
    chunk_text TEXT NOT NULL,
    chunk_type TEXT, -- definition, etymology, example, etc.
    chunk_size INTEGER,
    
    -- Embedding reference
    embedding_id TEXT,
    
    -- Indexing
    keywords TEXT, -- Space-separated keywords
    semantic_tags TEXT, -- JSON array of semantic tags
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (embedding_id) REFERENCES embeddings(document_id)
);



-- =======================
-- TRANSLATION MEMORY
-- =======================

-- Enhanced Translation Memory (TMX compatible)
CREATE TABLE IF NOT EXISTS translation_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Source and target
    source_text TEXT NOT NULL,
    target_text TEXT NOT NULL,
    source_lang TEXT NOT NULL, -- ISO 639-3 codes
    target_lang TEXT NOT NULL,
    
    -- Context and metadata
    domain TEXT, -- Semantic domain
    register TEXT, -- Formal/informal/ceremonial
    context TEXT, -- Surrounding text or situation
    
    -- Quality and provenance
    translation_quality TEXT CHECK (translation_quality IN ('excellent', 'good', 'acceptable', 'poor')),
    translator_id TEXT,
    translation_method TEXT, -- human, ai-assisted, machine
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    
    -- Links
    entry_id INTEGER, -- Link to main entry if applicable
    source_id INTEGER, -- Bibliographic source
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (entry_id) REFERENCES entries(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- =======================
-- SEMANTIC NETWORKS
-- =======================

-- Semantic Relations between Entries
CREATE TABLE IF NOT EXISTS semantic_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Related entries
    entry1_id INTEGER NOT NULL,
    entry2_id INTEGER NOT NULL,
    
    -- Relation type
    relation_type TEXT NOT NULL, -- synonym, antonym, hypernym, meronym, etc.
    relation_strength REAL CHECK (relation_strength BETWEEN 0.0 AND 1.0),
    
    -- Directionality
    bidirectional BOOLEAN DEFAULT TRUE,
    
    -- Context
    semantic_domain TEXT,
    cultural_context TEXT,
    
    -- Source
    source_id INTEGER,
    confidence TEXT CHECK (confidence IN ('high', 'medium', 'low')),
    
    FOREIGN KEY (entry1_id) REFERENCES entries(id),
    FOREIGN KEY (entry2_id) REFERENCES entries(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- =======================
-- USAGE EXAMPLES
-- =======================

-- Example Sentences and Usage
CREATE TABLE IF NOT EXISTS usage_examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    
    -- Example content
    miami_text TEXT NOT NULL,
    english_translation TEXT,
    french_translation TEXT,
    
    -- Linguistic analysis
    morpheme_breakdown TEXT,
    grammatical_analysis TEXT,
    
    -- Context
    context_type TEXT, -- conversation, narrative, ceremonial, etc.
    speaker_info TEXT,
    elicitation_context TEXT,
    
    -- Source
    source_id INTEGER,
    audio_file_path TEXT,
    
    -- Metadata
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
    pedagogical_notes TEXT,
    
    FOREIGN KEY (entry_id) REFERENCES entries(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- =======================
-- INDEXES FOR PERFORMANCE
-- =======================

-- Core indexes
CREATE INDEX IF NOT EXISTS idx_entries_headword ON entries(headword);
CREATE INDEX IF NOT EXISTS idx_entries_pos ON entries(pos);
CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status);

-- Etymology indexes
CREATE INDEX IF NOT EXISTS idx_etymologies_entry ON etymologies(entry_id);
CREATE INDEX IF NOT EXISTS idx_etymologies_proto ON etymologies(proto_language);

-- Phoneme indexes
CREATE INDEX IF NOT EXISTS idx_phonemes_ipa ON phonemes(ipa_symbol);
CREATE INDEX IF NOT EXISTS idx_phonemes_type ON phonemes(phoneme_type);

-- Source indexes
CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(source_type);
CREATE INDEX IF NOT EXISTS idx_sources_year ON sources(publication_year);
CREATE INDEX IF NOT EXISTS idx_entry_sources_entry ON entry_sources(entry_id);
CREATE INDEX IF NOT EXISTS idx_entry_sources_source ON entry_sources(source_id);

-- RAGLite indexes
CREATE INDEX IF NOT EXISTS idx_chunks_type ON document_chunks(chunk_type);
CREATE INDEX IF NOT EXISTS idx_chunks_source ON document_chunks(source_table, source_id);

-- Claude metadata indexes
CREATE INDEX IF NOT EXISTS idx_claude_session ON claude_metadata(session_id);
CREATE INDEX IF NOT EXISTS idx_claude_task ON claude_metadata(task_type);
CREATE INDEX IF NOT EXISTS idx_ai_contributions_table ON ai_contributions(table_name, record_id);

-- Translation memory indexes
CREATE INDEX IF NOT EXISTS idx_tm_source_lang ON translation_memory(source_lang);
CREATE INDEX IF NOT EXISTS idx_tm_target_lang ON translation_memory(target_lang);
CREATE INDEX IF NOT EXISTS idx_tm_domain ON translation_memory(domain);

-- Semantic relation indexes
CREATE INDEX IF NOT EXISTS idx_semantic_entry1 ON semantic_relations(entry1_id);
CREATE INDEX IF NOT EXISTS idx_semantic_entry2 ON semantic_relations(entry2_id);
CREATE INDEX IF NOT EXISTS idx_semantic_type ON semantic_relations(relation_type);

-- Usage example indexes
CREATE INDEX IF NOT EXISTS idx_examples_entry ON usage_examples(entry_id);
CREATE INDEX IF NOT EXISTS idx_examples_type ON usage_examples(context_type);

-- =======================
-- VIEWS FOR COMMON QUERIES
-- =======================

-- Complete entry view with all related data
CREATE VIEW IF NOT EXISTS complete_entries AS
SELECT 
    e.*,
    GROUP_CONCAT(DISTINCT s.title) as sources,
    GROUP_CONCAT(DISTINCT et.proto_form) as proto_forms,
    COUNT(DISTINCT ue.id) as example_count
FROM entries e
LEFT JOIN entry_sources es ON e.id = es.entry_id
LEFT JOIN sources s ON es.source_id = s.id
LEFT JOIN etymologies et ON e.id = et.entry_id
LEFT JOIN usage_examples ue ON e.id = ue.entry_id
GROUP BY e.id;

-- Phoneme inventory view
CREATE VIEW IF NOT EXISTS phoneme_inventory AS
SELECT 
    phoneme_type,
    COUNT(*) as count,
    GROUP_CONCAT(ipa_symbol, ', ') as symbols
FROM phonemes 
WHERE phonemic_status = 'phoneme'
GROUP BY phoneme_type;

-- =======================
-- LOCAL AI MODEL INTEGRATION
-- =======================

-- Ollama Models Configuration
CREATE TABLE IF NOT EXISTS ollama_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Model identification
    model_name TEXT NOT NULL UNIQUE, -- llama3.2, mistral, qwen2.5, etc.
    model_tag TEXT, -- latest, 7b, 13b, etc.
    model_family TEXT, -- llama, mistral, qwen, etc.
    model_size TEXT, -- 7B, 13B, 70B, etc.
    
    -- Capabilities
    supports_miami_illinois BOOLEAN DEFAULT FALSE,
    supports_translation BOOLEAN DEFAULT TRUE,
    supports_embeddings BOOLEAN DEFAULT FALSE,
    context_length INTEGER, -- Token context window
    
    -- Performance metrics
    tokens_per_second REAL,
    memory_usage_gb REAL,
    gpu_memory_required_gb REAL,
    
    -- Hardware compatibility
    requires_gpu BOOLEAN DEFAULT FALSE,
    supports_nvidia BOOLEAN DEFAULT TRUE,
    supports_axelera BOOLEAN DEFAULT FALSE,
    min_ram_gb INTEGER DEFAULT 8,
    
    -- Model status
    is_installed BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT FALSE,
    installation_path TEXT,
    last_used TIMESTAMP,
    
    -- Configuration
    temperature REAL DEFAULT 0.7,
    top_p REAL DEFAULT 0.9,
    top_k INTEGER DEFAULT 40,
    custom_params TEXT, -- JSON of additional parameters
    
    -- Performance tracking
    total_requests INTEGER DEFAULT 0,
    avg_response_time_ms REAL,
    success_rate REAL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- Hardware Configuration and Performance
CREATE TABLE IF NOT EXISTS hardware_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- System identification
    system_name TEXT NOT NULL,
    hostname TEXT,
    
    -- GPU Configuration
    gpu_count INTEGER DEFAULT 0,
    gpu_models TEXT, -- JSON array of GPU model names
    total_gpu_memory_gb REAL,
    nvidia_driver_version TEXT,
    cuda_version TEXT,
    
    -- Axelera AI Configuration
    axelera_chips INTEGER DEFAULT 0,
    axelera_model TEXT, -- M.2 accelerator model
    axelera_memory_gb REAL,
    axelera_driver_version TEXT,
    
    -- System specs
    cpu_model TEXT,
    cpu_cores INTEGER,
    system_ram_gb REAL,
    storage_type TEXT, -- SSD, NVMe, etc.
    
    -- Performance benchmarks
    inference_benchmark_score REAL,
    training_benchmark_score REAL,
    memory_bandwidth_gbps REAL,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_benchmark_date TIMESTAMP,
    
    -- Notes
    configuration_notes TEXT,
    optimization_flags TEXT,
    
    FOREIGN KEY (id) REFERENCES ollama_models(id)
);

-- =======================
-- WEBLATE INTEGRATION
-- =======================

-- Weblate Projects and Components
CREATE TABLE IF NOT EXISTS weblate_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Project identification
    weblate_project_id TEXT NOT NULL UNIQUE,
    project_name TEXT NOT NULL,
    project_slug TEXT NOT NULL,
    
    -- Language configuration
    source_language TEXT DEFAULT 'en', -- ISO 639-1
    target_languages TEXT, -- JSON array of target languages
    
    -- Component mapping
    component_name TEXT,
    component_slug TEXT,
    file_format TEXT, -- po, json, xliff, etc.
    
    -- Integration settings
    repository_url TEXT,
    branch_name TEXT DEFAULT 'main',
    file_mask TEXT, -- File pattern for translations
    
    -- Workflow configuration
    auto_accept_suggestions BOOLEAN DEFAULT FALSE,
    require_review BOOLEAN DEFAULT TRUE,
    enable_machine_translation BOOLEAN DEFAULT TRUE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_sync TIMESTAMP,
    sync_status TEXT CHECK (sync_status IN ('success', 'pending', 'failed')),
    
    -- Statistics
    total_strings INTEGER DEFAULT 0,
    translated_strings INTEGER DEFAULT 0,
    approved_strings INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Translation Workflow States
CREATE TABLE IF NOT EXISTS translation_workflow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Source reference
    entry_id INTEGER,
    translation_memory_id INTEGER,
    
    -- Weblate integration
    weblate_unit_id TEXT,
    weblate_project_id INTEGER,
    
    -- Translation states
    source_text TEXT NOT NULL,
    current_translation TEXT,
    
    -- Workflow status
    workflow_state TEXT CHECK (workflow_state IN ('new', 'needs_editing', 'translated', 'reviewed', 'approved', 'rejected')) DEFAULT 'new',
    priority TEXT CHECK (priority IN ('low', 'normal', 'high', 'urgent')) DEFAULT 'normal',
    
    -- Assignment
    assigned_translator TEXT,
    assigned_reviewer TEXT,
    
    -- Quality metrics
    translation_confidence REAL,
    fuzzy_match_score REAL,
    machine_translation_score REAL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    translated_at TIMESTAMP,
    reviewed_at TIMESTAMP,
    approved_at TIMESTAMP,
    
    -- Comments and notes
    translator_notes TEXT,
    reviewer_notes TEXT,
    context_notes TEXT,
    
    FOREIGN KEY (entry_id) REFERENCES entries(id),
    FOREIGN KEY (translation_memory_id) REFERENCES translation_memory(id),
    FOREIGN KEY (weblate_project_id) REFERENCES weblate_projects(id)
);

-- =======================
-- ENHANCED SPELLING RULES
-- =======================

-- Comprehensive Affix Rules (Miami-Illinois Spelling System)
CREATE TABLE IF NOT EXISTS affix_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Rule identification
    rule_name TEXT NOT NULL,
    rule_type TEXT CHECK (rule_type IN ('prefix', 'suffix', 'infix', 'stem_change', 'phonological')) NOT NULL,
    rule_category TEXT, -- inflection, derivation, phonological, etc.
    
    -- Affix details
    affix_form TEXT, -- The actual affix
    allomorphs TEXT, -- JSON array of variant forms
    orthographic_variants TEXT, -- Different spelling representations
    
    -- Phonological context
    phonological_environment TEXT, -- Where the rule applies
    preceding_context TEXT, -- What comes before
    following_context TEXT, -- What comes after
    
    -- Morphological conditions
    applies_to_pos TEXT, -- Part of speech it applies to
    stem_class_restrictions TEXT, -- Animate/inanimate, etc.
    semantic_restrictions TEXT,
    
    -- Rule operation
    input_pattern TEXT, -- Regex pattern for input
    output_pattern TEXT, -- Replacement pattern
    deletion_pattern TEXT, -- What to delete
    insertion_pattern TEXT, -- What to insert
    
    -- Aspell/Hunspell compatibility
    aspell_flag TEXT, -- Single character flag
    hunspell_flag TEXT, -- Hunspell flag code
    aspell_conditions TEXT, -- Aspell condition string
    hunspell_conditions TEXT, -- Hunspell condition string
    
    -- Rule properties
    productivity TEXT CHECK (productivity IN ('productive', 'semi-productive', 'irregular', 'suppletive')) DEFAULT 'productive',
    frequency TEXT CHECK (frequency IN ('common', 'uncommon', 'rare', 'archaic')) DEFAULT 'common',
    obligatory BOOLEAN DEFAULT TRUE,
    
    -- Exceptions and notes
    exceptions TEXT, -- JSON array of exception words
    irregular_forms TEXT, -- JSON array of irregular applications
    historical_notes TEXT,
    usage_notes TEXT,
    
    -- Examples
    example_base_forms TEXT, -- JSON array of base forms
    example_inflected_forms TEXT, -- JSON array of resulting forms
    example_sentences TEXT, -- JSON array of usage examples
    
    -- Ordering and priority
    rule_order INTEGER, -- Order of application
    priority INTEGER DEFAULT 50, -- Higher numbers = higher priority
    conflicts_with TEXT, -- JSON array of conflicting rule IDs
    
    -- Source and validation
    source_id INTEGER,
    confidence_level TEXT CHECK (confidence_level IN ('certain', 'probable', 'tentative', 'experimental')) DEFAULT 'probable',
    validation_status TEXT CHECK (validation_status IN ('validated', 'needs_testing', 'deprecated')) DEFAULT 'needs_testing',
    
    -- Statistics
    corpus_frequency INTEGER DEFAULT 0,
    accuracy_rate REAL, -- Success rate in spell checking
    false_positive_rate REAL,
    
    -- Metadata
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- Spell Check Results and Corrections
CREATE TABLE IF NOT EXISTS spell_check_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Input text
    original_text TEXT NOT NULL,
    corrected_text TEXT,
    
    -- Spell checking details
    words_checked INTEGER,
    errors_found INTEGER,
    corrections_applied INTEGER,
    
    -- Rules applied
    rules_triggered TEXT, -- JSON array of rule IDs that fired
    suggestions_generated TEXT, -- JSON array of suggestions
    
    -- User interaction
    user_accepted_corrections TEXT, -- JSON array of accepted suggestions
    user_rejected_corrections TEXT, -- JSON array of rejected suggestions
    user_custom_corrections TEXT, -- JSON array of user's own corrections
    
    -- Performance metrics
    processing_time_ms INTEGER,
    confidence_scores TEXT, -- JSON array of confidence per suggestion
    
    -- Context
    context_type TEXT, -- document_type, user_input, etc.
    user_id TEXT,
    session_id TEXT,
    
    -- Feedback for improvement
    feedback_provided BOOLEAN DEFAULT FALSE,
    feedback_text TEXT,
    correction_quality_rating INTEGER CHECK (correction_quality_rating BETWEEN 1 AND 5),
    
    -- Timestamps
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Morphological Analysis Cache
CREATE TABLE IF NOT EXISTS morphological_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Word form
    surface_form TEXT NOT NULL UNIQUE,
    normalized_form TEXT,
    
    -- Analysis results
    morphemes TEXT, -- JSON array of morpheme breakdown
    pos_tags TEXT, -- JSON array of possible POS tags
    grammatical_features TEXT, -- JSON of features (person, number, etc.)
    
    -- Possible analyses (for ambiguous forms)
    analyses TEXT, -- JSON array of all possible analyses
    preferred_analysis INTEGER, -- Index of preferred analysis
    
    -- Generation rules
    generation_rules TEXT, -- JSON array of rules used to generate this form
    base_form_id INTEGER, -- Link to entries table if available
    
    -- Validation
    human_verified BOOLEAN DEFAULT FALSE,
    confidence_score REAL,
    ambiguity_score REAL, -- How many analyses are possible
    
    -- Usage statistics
    frequency_rank INTEGER,
    corpus_count INTEGER DEFAULT 0,
    last_seen TIMESTAMP,
    
    -- Cache metadata
    analysis_version TEXT, -- Version of analyzer used
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (base_form_id) REFERENCES entries(id)
);

-- =======================
-- EXPORT AND INTEGRATION
-- =======================

-- Export Configurations
CREATE TABLE IF NOT EXISTS export_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Export target
    export_name TEXT NOT NULL,
    export_type TEXT CHECK (export_type IN ('claude_ai', 'huggingface', 'libretranslate', 'open_dataset', 'tmx', 'po', 'json', 'xml')) NOT NULL,
    
    -- Target platform settings
    platform_url TEXT,
    api_endpoint TEXT,
    authentication_method TEXT, -- api_key, oauth, basic_auth
    credentials_id TEXT, -- Reference to secure credential storage
    
    -- Export filters
    include_tables TEXT, -- JSON array of table names to include
    exclude_tables TEXT, -- JSON array of table names to exclude
    data_filters TEXT, -- JSON of WHERE clause conditions
    quality_threshold REAL, -- Minimum quality score for inclusion
    
    -- Format settings
    output_format TEXT, -- Specific format configuration
    encoding TEXT DEFAULT 'UTF-8',
    compression TEXT, -- none, gzip, zip
    
    -- Scheduling
    export_schedule TEXT, -- Cron-like schedule expression
    auto_export BOOLEAN DEFAULT FALSE,
    last_export TIMESTAMP,
    next_export TIMESTAMP,
    
    -- Validation
    validate_before_export BOOLEAN DEFAULT TRUE,
    validation_rules TEXT, -- JSON array of validation checks
    
    -- Statistics
    total_exports INTEGER DEFAULT 0,
    successful_exports INTEGER DEFAULT 0,
    last_export_size_mb REAL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Export History and Logs
CREATE TABLE IF NOT EXISTS export_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Export reference
    export_config_id INTEGER NOT NULL,
    
    -- Export details
    export_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    export_status TEXT CHECK (export_status IN ('started', 'in_progress', 'completed', 'failed', 'cancelled')) DEFAULT 'started',
    
    -- Data exported
    records_exported INTEGER DEFAULT 0,
    tables_exported TEXT, -- JSON array of exported table names
    export_file_path TEXT,
    export_file_size_mb REAL,
    
    -- Performance
    processing_time_seconds REAL,
    validation_time_seconds REAL,
    upload_time_seconds REAL,
    
    -- Results
    validation_results TEXT, -- JSON of validation check results
    error_messages TEXT, -- JSON array of any errors
    warnings TEXT, -- JSON array of warnings
    
    -- Target platform response
    platform_response TEXT, -- Response from target platform
    external_id TEXT, -- ID assigned by external platform
    public_url TEXT, -- Public URL if applicable
    
    -- Quality metrics
    data_quality_score REAL,
    completeness_percentage REAL,
    
    FOREIGN KEY (export_config_id) REFERENCES export_configs(id)
);

-- LibreTranslate Integration
CREATE TABLE IF NOT EXISTS libretranslate_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Server configuration
    server_url TEXT NOT NULL DEFAULT 'http://localhost:5000',
    api_key TEXT,
    
    -- Language support
    supported_languages TEXT, -- JSON array of supported language codes
    miami_illinois_supported BOOLEAN DEFAULT FALSE,
    custom_model_path TEXT, -- Path to custom Miami-Illinois model
    
    -- Translation settings
    default_source_lang TEXT DEFAULT 'mia',
    default_target_lang TEXT DEFAULT 'en',
    confidence_threshold REAL DEFAULT 0.7,
    
    -- Performance settings
    batch_size INTEGER DEFAULT 10,
    timeout_seconds INTEGER DEFAULT 30,
    max_retries INTEGER DEFAULT 3,
    
    -- Quality control
    enable_quality_estimation BOOLEAN DEFAULT TRUE,
    enable_post_editing BOOLEAN DEFAULT TRUE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_health_check TIMESTAMP,
    health_status TEXT CHECK (health_status IN ('healthy', 'degraded', 'unavailable')),
    
    -- Statistics
    total_translations INTEGER DEFAULT 0,
    successful_translations INTEGER DEFAULT 0,
    avg_response_time_ms REAL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =======================
-- ADDITIONAL INDEXES
-- =======================

-- Ollama and hardware indexes
CREATE INDEX IF NOT EXISTS idx_ollama_family ON ollama_models(model_family);
CREATE INDEX IF NOT EXISTS idx_ollama_active ON ollama_models(is_active);
CREATE INDEX IF NOT EXISTS idx_hardware_gpu ON hardware_config(gpu_count);

-- Weblate indexes
CREATE INDEX IF NOT EXISTS idx_weblate_project ON weblate_projects(weblate_project_id);
CREATE INDEX IF NOT EXISTS idx_workflow_state ON translation_workflow(workflow_state);
CREATE INDEX IF NOT EXISTS idx_workflow_priority ON translation_workflow(priority);

-- Spelling rule indexes
CREATE INDEX IF NOT EXISTS idx_affix_type ON affix_rules(rule_type);
CREATE INDEX IF NOT EXISTS idx_affix_pos ON affix_rules(applies_to_pos);
CREATE INDEX IF NOT EXISTS idx_affix_productivity ON affix_rules(productivity);
CREATE INDEX IF NOT EXISTS idx_affix_order ON affix_rules(rule_order);
CREATE INDEX IF NOT EXISTS idx_morph_surface ON morphological_analysis(surface_form);
CREATE INDEX IF NOT EXISTS idx_spell_check_date ON spell_check_log(checked_at);

-- Export indexes
CREATE INDEX IF NOT EXISTS idx_export_type ON export_configs(export_type);
CREATE INDEX IF NOT EXISTS idx_export_schedule ON export_configs(auto_export, next_export);
CREATE INDEX IF NOT EXISTS idx_export_history_config ON export_history(export_config_id);
CREATE INDEX IF NOT EXISTS idx_export_history_status ON export_history(export_status);

-- LibreTranslate indexes
CREATE INDEX IF NOT EXISTS idx_libretranslate_active ON libretranslate_config(is_active);

-- =======================
-- TRIGGERS FOR DATA INTEGRITY
-- =======================

-- Update timestamps
CREATE TRIGGER IF NOT EXISTS update_entries_timestamp 
AFTER UPDATE ON entries
BEGIN
    UPDATE entries SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_tm_timestamp 
AFTER UPDATE ON translation_memory
BEGIN
    UPDATE translation_memory SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_ollama_timestamp 
AFTER UPDATE ON ollama_models
BEGIN
    UPDATE ollama_models SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_affix_timestamp 
AFTER UPDATE ON affix_rules
BEGIN
    UPDATE affix_rules SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_morph_timestamp 
AFTER UPDATE ON morphological_analysis
BEGIN
    UPDATE morphological_analysis SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Increment usage count in translation memory
CREATE TRIGGER IF NOT EXISTS increment_tm_usage
AFTER INSERT ON translation_memory
BEGIN
    UPDATE translation_memory 
    SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Update model usage statistics
CREATE TRIGGER IF NOT EXISTS update_ollama_stats
AFTER INSERT ON claude_metadata
BEGIN
    UPDATE ollama_models 
    SET total_requests = total_requests + 1, last_used = CURRENT_TIMESTAMP 
    WHERE model_name = NEW.model_name;
END;
CREATE TABLE CopilotMetadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    confidence_score REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE AzureTranslateMetadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    source_language TEXT NOT NULL,
    target_language TEXT NOT NULL,
    translation_confidence REAL,
    request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Core Translation Memory (TMX-like) Tables
CREATE TABLE IF NOT EXISTS languages (
    lang_id INTEGER PRIMARY KEY AUTOINCREMENT,
    iso_639_3_code TEXT NOT NULL UNIQUE, -- e.g., 'en', 'mia', 'pot'
    bcp_47_tag TEXT UNIQUE,             -- e.g., 'en-US', 'mia-US', 'pot-us'
    language_name_en TEXT NOT NULL,     -- English name: e.g., 'English', 'Miami-Illinois'
    language_family TEXT,               -- e.g., 'Algic', 'Algonquian'
    notes TEXT
);

CREATE TABLE IF NOT EXISTS segments (
    segment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_language_code TEXT NOT NULL, -- FK to languages.iso_639_3_code
    target_language_code TEXT NOT NULL, -- FK to languages.iso_639_3_code
    source_text TEXT NOT NULL,
    target_text TEXT,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    quality_score REAL,                 -- e.g., 0.0 to 1.0 or 0 to 100
    translation_origin TEXT,            -- e.g., 'human', 'ollama_rag', 'google_translate', 'gemini'
    tmx_guid TEXT UNIQUE,               -- For TMX export/import round-tripping
    FOREIGN KEY (source_language_code) REFERENCES languages(iso_639_3_code),
    FOREIGN KEY (target_language_code) REFERENCES languages(iso_639_3_code)
);

CREATE TABLE IF NOT EXISTS tmx_files (
    tmx_file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT,                        -- e.g., 'imported', 'exported', 'error'
    source_locale TEXT,                 -- BCP 47 tag for TMX header
    target_locale TEXT,                 -- BCP 47 tag for TMX header
    version TEXT                        -- TMX version (e.g., '1.4')
);

-- RAG and Ollama Specific Tables
CREATE TABLE IF NOT EXISTS documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_name TEXT NOT NULL,
    document_path TEXT,                 -- Path to original file
    document_type TEXT,                 -- e.g., 'text', 'pdf', 'webpage', 'glossary'
    ingestion_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    source_language TEXT NOT NULL,      -- ISO 639-3 code
    notes TEXT
);

CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding BLOB,                     -- Store raw bytes of the embedding vector
    start_char_offset INTEGER,
    end_char_offset INTEGER,
    language_code TEXT NOT NULL,        -- ISO 639-3 code
    FOREIGN KEY (document_id) REFERENCES documents(document_id),
    FOREIGN KEY (language_code) REFERENCES languages(iso_639_3_code)
);

CREATE TABLE IF NOT EXISTS ollama_interactions (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    model_name TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    retrieved_chunk_ids TEXT,           -- Comma-separated list of chunk_id
    temperature REAL,
    top_p REAL,
    seed INTEGER
);

-- Linguistic Data Tables
CREATE TABLE IF NOT EXISTS lexicon (
    lex_id INTEGER PRIMARY KEY AUTOINCREMENT,
    language_code TEXT NOT NULL,        -- FK to languages.iso_639_3_code
    word TEXT NOT NULL COLLATE NOCASE,  -- Case-insensitive comparison for words
    phonetic_transcription TEXT,        -- e.g., IPA, Americanist
    part_of_speech TEXT,                -- e.g., 'N', 'V', 'Adj'
    definition_en TEXT,                 -- English definition
    notes TEXT,
    entry_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(language_code, word),
    FOREIGN KEY (language_code) REFERENCES languages(iso_639_3_code)
);

CREATE TABLE IF NOT EXISTS etymology (
    etym_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_lex_id INTEGER NOT NULL,     -- FK to lexicon.lex_id (e.g., original word)
    related_lex_id INTEGER NOT NULL,    -- FK to lexicon.lex_id (e.g., cognate in another language)
    relationship_type TEXT,             -- e.g., 'cognate', 'loanword', 'derivation'
    etymological_notes TEXT,
    FOREIGN KEY (source_lex_id) REFERENCES lexicon(lex_id),
    FOREIGN KEY (related_lex_id) REFERENCES lexicon(lex_id)
);

CREATE TABLE IF NOT EXISTS spelling_rules (
    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    language_code TEXT NOT NULL,        -- FK to languages.iso_639_3_code
    rule_type TEXT NOT NULL,            -- e.g., 'affix', 'compound', 'pronunciation'
    rule_definition TEXT NOT NULL,      -- The rule itself (e.g., pattern, description)
    example_words TEXT,                 -- Comma-separated examples
    notes TEXT,
    FOREIGN KEY (language_code) REFERENCES languages(iso_639_3_code)
);

-- Optional: For API output if needed, but TMX export is generally preferred
CREATE TABLE IF NOT EXISTS api_export_ready_translations (
    export_id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_segment_id INTEGER NOT NULL,
    api_source_text TEXT NOT NULL,
    api_target_text TEXT,
    api_source_lang TEXT NOT NULL,
    api_target_lang TEXT NOT NULL,
    detected_source_lang TEXT,
    api_service_used TEXT,
    api_response_metadata TEXT, -- JSON blob of full API response or relevant parts
    export_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (original_segment_id) REFERENCES segments(segment_id)
);

CREATE TABLE IF NOT EXISTS api_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_service TEXT NOT NULL,         -- e.g., 'gemini', 'google_translate'
    endpoint TEXT,                     -- e.g., '/v1/models/gemini-pro:generateContent', '/language/translate/v2'
    request_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    response_timestamp DATETIME,
    request_payload TEXT,              -- The JSON sent to the API
    response_payload TEXT,             -- The JSON received from the API
    http_status_code INTEGER,
    error_message TEXT,                -- Any error message if the call failed
    duration_ms INTEGER,               -- Milliseconds for the API call
    user_id INTEGER,                   -- Optional: if linking to a user in your system
    session_id TEXT,                   -- Optional: if tracking user sessions
    notes TEXT
);

CREATE TABLE IF NOT EXISTS translations (
    translation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_id INTEGER,                     -- FK to api_logs.log_id if this translation came from an API call
    source_language TEXT NOT NULL,      -- ISO 639-1 or BCP-47 (e.g., 'en', 'en-US')
    target_language TEXT NOT NULL,      -- ISO 639-1 or BCP-47 (e.g., 'es', 'es-MX')
    original_text TEXT NOT NULL,
    translated_text TEXT,
    translation_method TEXT,            -- e.g., 'google_translate_api', 'gemini_api', 'cached', 'manual'
    confidence_score REAL,              -- For services that provide it (e.g., Google Translate sometimes gives detection confidence)
    characters_billed INTEGER,          -- Characters sent/received, useful for billing tracking
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (log_id) REFERENCES api_logs(log_id)
);

CREATE TABLE IF NOT EXISTS gemini_interactions (
    gemini_id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_id INTEGER,                     -- FK to api_logs.log_id
    model_name TEXT NOT NULL,           -- e.g., 'gemini-pro', 'gemini-1.5-flash'
    input_prompt TEXT NOT NULL,         -- The primary prompt sent to Gemini
    response_text TEXT,                 -- The main generated response
    generation_settings TEXT,           -- JSON string of settings (e.g., temperature, top_k, top_p, max_output_tokens)
    safety_ratings TEXT,                -- JSON string of safety ratings from Gemini's response
    usage_metadata TEXT,                -- JSON string for token counts (input, output, total)
    finish_reason TEXT,                 -- e.g., 'STOP', 'MAX_TOKENS', 'SAFETY', 'RECITATION'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (log_id) REFERENCES api_logs(log_id)
);

CREATE TABLE IF NOT EXISTS google_translate_glossaries (
    glossary_id TEXT PRIMARY KEY,       -- Google's unique ID for the glossary (e.g., projects/PROJECT_NUMBER/locations/LOCATION/glossaries/GLOSSARY_ID)
    display_name TEXT NOT NULL,
    source_language TEXT NOT NULL,
    target_language TEXT NOT NULL,
    creation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_update_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    entry_count INTEGER,                -- Number of terms in the glossary
    notes TEXT
);

CREATE TABLE IF NOT EXISTS google_translate_terms (
    term_entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    glossary_id TEXT NOT NULL,          -- FK to google_translate_glossaries.glossary_id
    source_term TEXT NOT NULL,
    target_term TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (glossary_id) REFERENCES google_translate_glossaries(glossary_id)
);

-- Revised or central translation record
CREATE TABLE IF NOT EXISTS translations (
    translation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_language_code TEXT NOT NULL, -- e.g., 'en-US', 'mia'
    target_language_code TEXT NOT NULL, -- e.g., 'mia', 'en-US'
    source_text TEXT NOT NULL,
    translated_text TEXT,
    translation_origin TEXT NOT NULL,   -- e.g., 'human', 'ollama_rag', 'google_translate', 'gemini'
    translation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    quality_score REAL,                 -- Human or AI confidence score

    -- Links to specific API interactions or TMX data
    google_translate_request_id INTEGER, -- FK to google_translate_requests.request_id
    gemini_request_id INTEGER,           -- FK to gemini_requests.request_id
    tmx_segment_id_ref TEXT,             -- For referencing original TMX segments, or a specific local segment ID if you keep a `local_tmx_segments` table

    FOREIGN KEY (google_translate_request_id) REFERENCES google_translate_requests(request_id),
    FOREIGN KEY (gemini_request_id) REFERENCES gemini_requests(request_id)
    -- Consider FK to your local TMX segment ID if you prefer to decouple `translations` from `segments`
);
INSERT OR IGNORE INTO languages (iso_639_3_code, bcp_47_tag, language_name_en, language_family, notes) VALUES
('en', 'en-US', 'English', 'Indo-European', 'US English locale for BCP 47 compliance.'),
('mia', 'mia-US', 'Myaamia', 'Algic', 'Myaamia language, primarily US usage.'),
('pot', 'pot-US', 'Potawatomi', 'Algic', 'Potawatomi language, primarily US usage (Michigan/Northern Indiana).'),
('kic', 'kic-US', 'Kickapoo', 'Algic', 'Kickapoo language, primarily US usage.'),
('sac', 'sac-US', 'Meskwaki', 'Algic', 'Meskwaki (Fox, Sauk) language, primarily US usage.'),
('ciw', 'ciw-US', 'Chippewa', 'Algic', 'Chippewa (Ojibwe) language, specifically US usage.'), -- Use 'ciw' for US Ojibwe dialects
('crk', 'crk-US', 'Plains Cree', 'Algic', 'Plains Cree language, primarily US usage/border regions.'); -- Example Cree dialect for US


-- Translation pairs (aligned for ChatGPT or TMX export)
CREATE TABLE IF NOT EXISTS translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_lang TEXT NOT NULL,
    target_lang TEXT NOT NULL,
    source_text TEXT NOT NULL,
    target_text TEXT NOT NULL,
    alignment_note TEXT,         -- e.g. exact, inferred, gloss, etc.
    domain TEXT,                 -- e.g. ceremonial, conversational, botanical
    context TEXT,                -- optional free text or usage info
    source_ref TEXT,             -- shortref to corpus_sources
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
