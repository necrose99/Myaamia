-- =======================
-- BIBLIOGRAPHIC TABLES
-- =======================

-- Sources and References
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Basic bibliographic info
    title TEXT NOT NULL,
    author TEXT,
    editor TEXT,
    publication_year INTEGER,
    publisher TEXT,
    publication_place TEXT,
    
    -- Source details
    source_type TEXT CHECK (source_type IN ('book', 'article', 'thesis', 'manuscript', 'dictionary', 'grammar', 'fieldwork', 'archive', 'oral')),
    pages TEXT, -- Page range or total pages
    volume TEXT,
    issue TEXT,
    
    -- Digital identifiers
    isbn TEXT,
    doi TEXT,
    url TEXT,
    archive_location TEXT,
    
    -- Language documentation specifics
    consultant_info TEXT, -- Speaker information
    recording_date TEXT,
    fieldwork_location TEXT,
    
    -- Quality and reliability
    reliability_rating INTEGER CHECK (reliability_rating BETWEEN 1 AND 5),
    peer_reviewed BOOLEAN DEFAULT FALSE,
    primary_source BOOLEAN DEFAULT FALSE,
    
    -- Notes
    notes TEXT,
    abstract TEXT,
    
    -- Metadata
    added_by TEXT,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
