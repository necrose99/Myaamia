-- 1. Master Identity Core Table (Deduplicated Languoid Nodes)
CREATE TABLE IF NOT EXISTS languoids (
    glottocode TEXT PRIMARY KEY CHECK(length(glottocode) = 8),
    iso_639_3 CHAR(3),
    wikidata_id TEXT,
    wals_code TEXT,
    display_name TEXT NOT NULL,
    subfamily_group TEXT,
    latitude REAL,
    longitude REAL
);

-- 2. Ontolex-Lemon Morphological Core (For etymological tracking)
CREATE TABLE IF NOT EXISTS lexical_entries (
    entry_id TEXT PRIMARY KEY,
    glottocode TEXT REFERENCES languoids(glottocode),
    written_rep TEXT NOT NULL,         -- e.g., "Hinónoʼeitíít"
    morpheme_glos TEXT,                -- Interlinear Morpheme Translation
    etymon_target TEXT,                -- Points back to Proto-Algonquian root if known
    FOREIGN KEY(glottocode) REFERENCES languoids(glottocode)
);

-- 3. External Metrics/Grambank Features JSON Cache
CREATE TABLE IF NOT EXISTS feature_matrix (
    glottocode TEXT PRIMARY KEY,
    grambank_json TEXT,                -- Caches v1.0.3 structural profile parameters
    elp_status TEXT,                   -- Endangered Languages Project Vitality
    FOREIGN KEY(glottocode) REFERENCES languoids(glottocode)
);

-- Indexes optimized specifically for UI hovers and etymological lookups
CREATE INDEX IF NOT EXISTS idx_iso_lookup ON languoids(iso_639_3);
CREATE INDEX IF NOT EXISTS idx_etymon ON lexical_entries(etymon_target);
