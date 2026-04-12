---
name: olac_import
description: |
  OLAC Ingestion Skill for Myaamia and Algonquian Language Revitalization.
  Harvests linguistic data from OLAC, extracts lexical items, generates BabelEdit JSONs (with all supervisors),
  exports LEMON/OntoLex RDF using lemon-model.net, and prepares basic Hunspell dictionaries.
  Integrates with FLEx (via your XSLT suite for LIFT/TMX) and keeps everything local.
user-invocable: true
command-dispatch: tool
command-tool: exec
command-arg-mode: raw
---

# OLAC Import Skill

## Purpose
Use this skill whenever you need to refresh linguistic data for Myaamia (mia), other Algonquian languages, or supervisor layers (English, Old French 1600s, Latin for scientific names, etc.).

## How to Invoke
Call the skill with a raw command like one of these:

- `python3 scripts/OLAC_import.py harvest --max 400`
- `python3 scripts/OLAC_import.py extract`
- `python3 scripts/OLAC_import.py babeledit`
- `python3 scripts/OLAC_import.py lemon`
- `python3 scripts/OLAC_import.py hunspell`
- `python3 scripts/OLAC_import.py full --max 500`

## What Each Command Does
- **harvest** — Pulls fresh records from OLAC OAI-PMH
- **extract** — Turns raw records into usable word/concept pairs
- **babeledit** — Creates one JSON per language + empty supervisor files (perfect for Generic JSON project in BabelEdit)
- **lemon** — Exports full LEMON RDF (Turtle + RDF/XML) with Lexicon, LexicalEntry, Form, and LexicalSense structures
- **hunspell** — Generates a basic .dic word list for Myaamia spell-checking
- **full** — Runs the entire pipeline in one go

## Output Locations
- `babeledit_algonquian/` → JSON files for BabelEdit
- `output/myaamia_lexicon.ttl` + `.rdf` → LEMON semantic lexicon
- `hunspell/myaamia.dic` → Hunspell dictionary
- `data/olac_data.db` → Persistent SQLite cache

## Tips for the Agent
- Always run `harvest` then `extract` before other outputs.
- After running, you can chain with your XSLT suite for LIFT ↔ TMX conversions.
- The LEMON export links words to concepts and tags supervisor languages clearly.
- All operations stay fully local.

This skill keeps your FLEx lexicon, BabelEdit projects, and semantic RDF layer up to date with minimal manual effort.
