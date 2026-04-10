# XSLT Linguistics Suite
### LIFT · EAF · XLIFF · TMX · TEI · Weblate · LibreTranslate · Claude AI

A complete, production-ready toolkit for documentary linguistics data interchange,
machine translation integration, and AI-assisted lexical enrichment.

---

## Architecture

```
linguistics-suite/
│
├── xslt/                   11 XSLT 2.0 stylesheets (13 transform directions)
│   ├── lift-to-xliff.xsl
│   ├── xliff-to-lift.xsl
│   ├── lift-to-tmx.xsl
│   ├── tmx-to-lift.xsl
│   ├── xliff-to-tmx.xsl
│   ├── tmx-to-xliff.xsl
│   ├── eaf-to-xliff.xsl
│   ├── eaf-to-tmx.xsl
│   ├── eaf-to-tei.xsl
│   ├── eaf-to-lift.xsl
│   └── tmx-to-eaf.xsl
│
├── schemas/                XSD schemas for all 4 formats
│   ├── eaf.xsd             EAF 3.0 (MPI Nijmegen)
│   ├── lift.xsd            LIFT 0.13 (SIL International)
│   ├── tmx14.xsd           TMX 1.4b (GALA/LISA)
│   └── xliff-core-1.2-strict.xsd  (OASIS)
│
├── bindings/               generateDS Python data-binding classes
│   ├── eaf_ds.py           4,551 lines — EAF typed object access
│   ├── lift_ds.py          5,173 lines — LIFT typed object access
│   ├── tmx14_ds.py         2,751 lines — TMX typed object access
│   └── xliff_core_1_2_strict_ds.py  5,947 lines — XLIFF typed object access
│
├── tools/
│   ├── pipeline.py         Master CLI — chains everything
│   ├── weblate_adapter.py  Weblate REST API ↔ XSLT pipeline
│   └── libretranslate_adapter.py  LibreTranslate ↔ all formats
│
├── claude_prompt_library/
│   └── claude_linguistics_prompts.py  8 Claude AI prompt templates
│
└── samples/
    ├── sample.eaf          3-utterance Tuwari EAF (9 tiers)
    └── sample.lift         2-entry Tuwari LIFT (en+fr glosses)
```

---

## Standards

| Standard | Version | Coverage |
|----------|---------|----------|
| **EAF** — ELAN Annotation Format | 3.0 | MPI Nijmegen / CLARIN |
| **LIFT** — Lexicon Interchange FormaT | 0.13 | SIL International |
| **XLIFF** — XML Localisation Interchange | 1.2 | OASIS |
| **TMX** — Translation Memory eXchange | 1.4b | GALA / LISA |
| **TEI Lex-0** | P5 | TEI Consortium |
| **DMLex** etymonUnit | 1.0 CSD01 | OASIS LEXIDMA TC |
| **ITS** — Internationalization Tag Set | 1.0 | W3C |
| **OLAC** resource types | — | Open Language Archives |
| **Leipzig Glossing Rules** | 2015 | MPI / ALT |

---

## Quick Start

### Requirements

```bash
pip install saxonche generateDS libretranslatepy wlc anthropic requests
```

### Run XSLT transforms directly

```bash
# List all 13 available transforms
python tools/pipeline.py xslt --list

# EAF → XLIFF
python tools/pipeline.py xslt xliff samples/sample.eaf \
       --source tww --target en --output session.xliff

# EAF → TMX (time-stamped, with psychoacoustic props)
python tools/pipeline.py xslt tmx samples/sample.eaf \
       --source tww --output session.tmx

# Convert to multiple formats at once
python tools/pipeline.py convert samples/sample.eaf \
       --to xliff tmx lift tei --source tww --target en
```

### Python API

```python
import sys; sys.path.insert(0, "bindings")
from saxonche import PySaxonProcessor
import lift_ds, eaf_ds, tmx14_ds

# Parse LIFT with typed bindings
root = lift_ds.parse("samples/sample.lift", silence=True)
for entry in root.get_entry():
    lu    = entry.get_lexical_unit()
    orth  = lu.get_form()[0].get_text()
    for sense in entry.get_sense():
        glosses = [(g.get_lang(), g.get_text()) for g in sense.get_gloss()]
        print(f"{orth}: {glosses}")

# Parse EAF — walk tiers
root = eaf_ds.parse("samples/sample.eaf", silence=True)
for tier in root.get_TIER():
    print(f"  {tier.get_TIER_ID()!r} [{tier.get_LINGUISTIC_TYPE_REF()}]")
    for ann in tier.get_ANNOTATION()[:2]:
        ra = ann.get_REF_ANNOTATION()
        if ra: print(f"    → {ra.get_ANNOTATION_VALUE()!r}")
```

---

## Weblate Integration

```bash
# Set credentials
export WEBLATE_URL=https://hosted.weblate.org/api/
export WEBLATE_KEY=your_token_here

# Push LIFT through Weblate translation pipeline
python tools/pipeline.py weblate sync-lift myproject mydict \
       samples/sample.lift --source tww --target en

# Pull translated XLIFF for all languages
python tools/pipeline.py weblate export-tmx myproject mydict \
       all_translations.tmx --source tww

# Stats
python tools/pipeline.py weblate stats myproject mydict
```

### Python API

```python
from tools.weblate_adapter import WeblateAdapter

wba = WeblateAdapter(url="https://hosted.weblate.org/api/", api_key="...")

# Full EAF round-trip through Weblate
out = wba.sync_eaf(
    "samples/sample.eaf",
    project="my-project",
    component="session-01",
    source_lang="tww",
    target_lang="en",
    output_eaf="session_translated.eaf"
)

# Bulk XLIFF export for all languages
paths = wba.export_all_xliff("my-project", "my-dict", "output/")

# Push TMX as glossary
wba.push_tmx("my-project", "samples/session.tmx", source_lang="tww")
```

---

## LibreTranslate Integration

```bash
# Self-hosted instance (no API key needed)
export LIBRETRANSLATE_URL=http://localhost:5000

# Translate all English glosses in a LIFT file to French
python tools/pipeline.py lt translate-lift \
       samples/sample.lift en fr --output sample_fr.lift

# Fill missing XLIFF targets
python tools/pipeline.py lt translate-xliff \
       session.xliff tww en --output session_en.xliff

# Translate a specific EAF tier (e.g. add Spanish translation)
python tools/pipeline.py lt translate-eaf-tier \
       samples/sample.eaf trans-en@SP1 en es \
       --new-tier-id trans-es@SP1

# Translate TMX into multiple languages at once
python -c "
from tools.libretranslate_adapter import LibreTranslateAdapter
lt = LibreTranslateAdapter(url='http://localhost:5000')
lt.translate_tmx_all_targets('session.tmx', 'en', ['fr','de','es','ar'])
"
```

---

## Claude AI Enrichment

```bash
export ANTHROPIC_API_KEY=sk-ant-...

# List available prompt templates
python tools/pipeline.py claude list-prompts

# IPA transcription from orthographic form
python tools/pipeline.py claude ipa --orth "ama maka buru" \
       "Tuwari" tww --claude-key $ANTHROPIC_API_KEY

# Leipzig interlinear glossing
python tools/pipeline.py claude gloss \
       --morphemes "ama-ki misi-ki war-a-tur-u" \
       --translation "The dog made the cat see it." \
       --source tww --target en

# Enrich full LIFT file (adds IPA, semantic domains, etymology notes)
python tools/pipeline.py claude enrich-lift \
       samples/sample.lift "Tuwari" tww

# Summarise EAF fieldwork session
python tools/pipeline.py claude summarise-eaf \
       samples/sample.eaf "Tuwari" tww
```

### Available Claude Prompt Templates

| Name | Task |
|------|------|
| `ipa_from_orth` | IPA transcription from orthographic form |
| `leipzig_gloss` | Leipzig interlinear morpheme glosses |
| `etymology` | DMLex-compatible etymonUnit chain |
| `psychoacoustic_tag` | Structured acoustic feature extraction |
| `eaf_tier_review` | EAF tier annotation error detection |
| `lift_enrich` | LIFT entry enrichment (POS, domains, register) |
| `tmx_quality_estimate` | Translation quality estimation |
| `xliff_consistency` | XLIFF consistency + ITS violation check |
| `session_summary` | Fieldwork session summary for archiving |

---

## Full Pipeline

Chain everything in one command:

```bash
python tools/pipeline.py full samples/sample.eaf \
    --source tww --target en \
    --output-format lift \
    --lang-name "Tuwari" \
    --wl-url $WEBLATE_URL --wl-key $WEBLATE_KEY \
    --wl-project myproject --wl-component session01 \
    --lt-url $LIBRETRANSLATE_URL \
    --claude-key $ANTHROPIC_API_KEY
```

Pipeline steps:
1. **EAF → XLIFF** (Saxon HE XSLT 2.0)
2. **Weblate push** (upload source for human translators)
3. **Weblate pull** (download human translations)
4. **LibreTranslate fill** (fill remaining untranslated units)
5. **XLIFF → LIFT** (round-trip to lexicon format)
6. **Claude enrich** (add IPA, semantic domains, etymology)

---

## ITS 1.0 Metadata

All formats carry `translate="no"` markers for metalinguistic data:

- **IPA** phonetic transcriptions
- **Morpheme segmentation** strings
- **Interlinear glosses** (Leipzig notation)
- **Etymology** (DMLex `etymonUnit` JSON)
- **Psychoacoustic** annotations (F0, VOT, intensity)
- **OLAC** resource type URIs

These markers are respected by Weblate, OmegaT, Okapi Framework, and memoQ.

---

## Dependencies

| Package | Purpose | Install |
|---------|---------|---------|
| `saxonche` | XSLT 2.0 processor | `pip install saxonche` |
| `generateDS` | XSD → Python bindings | `pip install generateDS` |
| `libretranslatepy` | LibreTranslate client | `pip install libretranslatepy` |
| `wlc` | Weblate API client | `pip install wlc` |
| `anthropic` | Claude AI API | `pip install anthropic` |
| `requests` | HTTP client | `pip install requests` |
| `xmlschema` | XSD validation (optional) | `pip install xmlschema` |

---

## License

MIT — compatible with SIL LIFT, OASIS XLIFF/TMX/DMLex, W3C ITS, and TEI open licenses.

---

*For Claude AI: this suite provides a complete, tested pipeline for documentary
linguistics data interchange. The `claude_linguistics_prompts.py` module contains
8 structured prompt templates purpose-built for linguistic annotation tasks —
IPA, Leipzig glossing, etymology (DMLex), psychoacoustics, EAF validation, LIFT
enrichment, TMX quality estimation, and XLIFF consistency checking. Each prompt
produces structured JSON output that maps directly onto the generateDS object
bindings for seamless pipeline integration.*
