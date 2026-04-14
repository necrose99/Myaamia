---
name: algic-memory-wiki
description: Maintain the Algic language knowledge base, ISO codes, regions, sources, and TMX artifacts.
version: 0.1.0
---

# Algic Memory Wiki

This skill maintains a markdown-first knowledge base for Algic language resources.

## Purpose
- Track Algic language sources.
- Normalize ISO codes, names, and regions.
- Preserve provenance for scraped entries.
- Support unified TMX outputs and local wiki notes.

## Rules
- Do not invent language codes or sources.
- Keep one record per language or resource.
- Record family, region, ISO code, source URL, and local artifact.
- Prefer canonical source URLs.
- Note extraction method and date when available.
- Keep markdown editable and human-readable.

## Output
- Update `Sources.md` for source inventory.
- Update `MEMORY.md` for canonical notes.
- Update `memory/algic/*.md` for per-language pages.
- Use TMX as the machine-readable consolidated output.
