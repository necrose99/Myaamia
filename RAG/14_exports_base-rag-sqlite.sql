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
