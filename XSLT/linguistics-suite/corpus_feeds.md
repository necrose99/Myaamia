# corpus_feeds.md
## Algonquian NLP Pipeline — Data Source Registry
## Status: active | pending | requested | blocked | done

---

### Miami-Illinois (mia) — PRIMARY

#### necrose99/Myaamia GitHub repo
- [x] ILDA dictionary hand-scraped → TMX
      file: Myaamia-lda-dictionary.tmx
      status: DONE — normalize through XSLT pipeline
- [x] Weblate memory exports
      files: *-weblate-memory.tmx, Myaamia-omegat.tmx
      status: DONE — merge + deduplicate
- [x] FLEx backup 2024-07-03
      file: Myaamia 2024-07-03 1957.fwbackup
      status: UNPROCESSED — highest priority
      action: unzip → export LIFT via FLEx natively
- [x] OmegaT project TMs
      dir: omegat/, tm/
      status: DONE — run tmx_to_ollama_jsonl.py
- [ ] ILDA entry subpages (full structured entries)
      url: mc.miamioh.edu/ilda-myaamia/dictionary/entries/[id]
      robots.txt: BLOCKED
      action: email myaamiacenter@miamioh.edu
               — show GitHub repo, request LIFT/JSON export
               — peer contribution framing, not cold scrape

#### Myaamia Center digital resources
- [ ] MIDA (Miami-Illinois Digital Archive)
      url: miamioh.edu/myaamia-center/research/digital-resources
      status: pending contact
- [ ] mahkihkiwa ethnobotanical database
      status: pending contact — could add semantic domain data

---

### Ojibwe (ojp / alq)

- [ ] Ojibwe People's Dictionary
      url: ojibwemowin.com
      format: structured HTML → LIFT
      priority: HIGH — quality controlled, audio-linked
      orthography: Fiero double-vowel (standard)
      spider: scrapy/opd_spider.py (TODO)
- [ ] Anishinaabemodaa parallel stories
      url: anishinaabemodaa.ca
      format: bilingual HTML → TMX
      priority: HIGH — running text not just wordlists
- [ ] Baraga's dictionary (1850)
      url: Project Gutenberg PD
      format: OCR'd text → manual normalization → LIFT
      orthography: 19th century mission — normalize to Fiero

---

### Sac-Fox / Meskwaki (sac)

- [ ] Community workbook PDF
      format: PDF interlinear → pdfplumber → LIFT
      parser: tools/sac_workbook_parser.py (READY)
      lang_code: sac
      orthography: practical-roman
      note: same parser handles kic, mia PDFs with --lang flag
- [ ] NAA Michelson collection
      source: Smithsonian National Anthropological Archives
      format: PDF/digitized interlinear → EAF
      status: PD — request digitized scans
      orthography: Bloomfield → normalize to SRO
      priority: HIGH — morphologically dense, PD
- [ ] Meskwaki syllabary materials
      status: research needed — Unicode normalizer required first
      blocker: syllabary → Unicode mapping incomplete

---

### Potawatomi (pot)

- [ ] SIL Potawatomi materials
      source: SIL archive — may have LIFT exports natively
      status: pending research
      note: SIL toolchain → LIFT is natural fit
- [ ] Pokagon Band language program
      status: pending contact
      orthography: Fiero variant

---

### Kickapoo (kic)

- [ ] Voorhis manuscripts (1970s-80s)
      source: University of Kansas linguistics archive
      format: manuscript/PDF → manual
      status: pending archive contact
- [ ] AILLA Kickapoo deposits
      url: ailla.utexas.org
      status: request access
      priority: Mexico variety if available — most conservative
- [ ] SIL Oklahoma Kickapoo work
      status: pending research — may have LIFT already
- [ ] Community workbook if exists
      parser: tools/sac_workbook_parser.py --lang kic (READY)

---

### Cross-family Etymology

- [ ] Wiktionary Proto-Algonquian reconstructions
      url: en.wiktionary.org/wiki/Category:Proto-Algonquian_reconstructions
      api: api.php?action=parse&format=json
      output: DMLex etymonUnit JSON → SQLite cognate_set
      spider: scrapy/wiktionary_pa_spider.py (TODO)
      scope: ~500-800 entries, bounded and manageable
      priority: GOOD FIRST FOOTHILL — bounded, clean API

---

### SQLite Schema Target

```sql
CREATE TABLE language (
    id          TEXT PRIMARY KEY,  -- ISO 639-3
    family      TEXT,              -- Algonquian
    subfamily   TEXT,              -- Sac-Fox-Kickapoo, Central, etc
    orthography TEXT               -- fiero, practical-roman, syllabics
);

CREATE TABLE cognate_set (
    id           INTEGER PRIMARY KEY,
    proto_form   TEXT,    -- PA reconstruction *form
    proto_gloss  TEXT,
    confidence   REAL,
    source_ref   TEXT
);

CREATE TABLE cognate_member (
    cognate_set_id INTEGER REFERENCES cognate_set(id),
    language_id    TEXT    REFERENCES language(id),
    surface_form   TEXT,
    source_ref     TEXT,
    lift_entry_id  TEXT
);
```

---

### Mt Everest (not today, noted for later)

- Full PA reconstruction database integration
- Meskwaki syllabary → Unicode normalizer
- Montreal Forced Aligner hook (audio segmentation)
- Cross-family comparative (Wiyot/Yurok distant relatives)
- Real-time Weblate ↔ ELAN sync
- FR/EN/ES parallel corpus for cross-pairs
- Psychoacoustic F0 extraction automation (Praat/Parselmouth)
