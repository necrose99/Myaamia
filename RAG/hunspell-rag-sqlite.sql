--- https://github.com/necrose99/Myaamia/tree/master/Aspell-Hunspell
--- https://github.com/necrose99/Myaamia/blob/master/Aspell-Hunspell/MIA_US-Myaamia.dic
-- https://github.com/necrose99/Myaamia/blob/master/Aspell-Hunspell/MIA_US-Myaamia.aff 
--- from tmx etc export imporve aff rules on export and comented MIA_US-Myaamia.dic ie mia_word #english-meaning/deifintion for hunspell. 

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
