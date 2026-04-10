# Algonquian NLP Pipeline — Conversation Notes
## Session: XSLT Linguistics Suite Development

### What was built
- 11 XSLT 2.0 stylesheets — 13 bidirectional transform directions
  LIFT ↔ XLIFF ↔ TMX ↔ EAF ↔ TEI
- 4 XSD schemas (EAF 3.0, LIFT 0.13, TMX 1.4b, XLIFF 1.2)
- 4 generateDS Python bindings (~18k lines typed object access)
- weblate_adapter.py — full REST API integration
- libretranslate_adapter.py — MT at format object level
- claude_linguistics_prompts.py — 9 prompt templates
- pipeline.py — master CLI chaining everything
- syllabics_transliterator.html — furigana-style hover tooltip
- tmx_to_ollama_jsonl.py — fine-tune dataset builder
- sac_workbook_parser.py — PDF workbook → LIFT

### Target language family
- Algonquian / Central Algonquian focus
- Miami-Illinois (mia) — necrose99/Myaamia repo, hand-scraped ILDA
- Ojibwe (ojp) — OPD priority scrape target
- Potawatomi (pot) — conservative PA features, good anchor
- Meskwaki / Sac-Fox (sac) — Michelson collection, syllabary
- Kickapoo (kic) — Mexico variety most conservative
- Cree syllabics — covered by transliterator tool

### Data sources identified
- necrose99/Myaamia — existing TMX corpus, FLEx backup (UNPROCESSED)
- ILAD / mc.miamioh.edu — robots.txt blocked, contact route preferred
  myaamiacenter@miamioh.edu
- Ojibwe People's Dictionary (ojibwemowin.com) — priority scrape
- Anishinaabemodaa — parallel stories, scrapeable
- NAA Michelson Meskwaki collection — Smithsonian, PD
- Sac-Fox community workbook PDF — pdfplumber parser ready
- Wiktionary Proto-Algonquian — etyl:alg spider planned
- AILLA deposits — request route for EAF materials

### Architecture roadmap
```
Scrapy spiders → LIFT XML (generateDS)
                      ↓
              XSLT normalize suite
                      ↓
              SQLite cognate_set schema
              (language, cognate_set, cognate_member tables)
                      ↓
              tmx_to_ollama_jsonl.py
                      ↓
              llama.cpp fine-tune (AM4/RTX2070 slow burn)
                      ↓
              GGUF model → Ollama
                      ↓
              Axelera 4x AIPU bundle (future gift box)
              for Myaamia Center
```

### Hardware context
- Current: Exaviz Cruiser CM5 + Axelera Metis M.2 (Frigate/HA NVR)
- RPi5 blade rack — Zabbix, Zentyal, PoE infra
- AM4 desktop + RTX2070 — Ollama slow-burn when AM5 migration happens
- AM5 target — RTX5070 for FFXIV weekends
- AM4 repurpose: Gentoo binhost OR Algonquian language AI box
- Dream gift: Axelera 4x AIPU bundle → Myaamia Center fully loaded

### Key insight
Polysynthetic languages break standard NLP tokenizers.
The XSLT suite normalizes morpheme boundaries explicitly
via ITS translate="no" on IPA/gloss/morph/etymology tiers
BEFORE data reaches the model — giving Ollama structured
linguistic signal rather than surface form pattern matching.

### corpus_feeds.md — see separate file

### šooli
When the cybersecurity architect role lands,
the Axelera bundle goes to the Myaamia Center.
That's the goal.

  Aya — the work matters.
