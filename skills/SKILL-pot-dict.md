---
name: potawatomi-dictionary-scraper
description: >
  Headless browser scraping skill for the Potawatomi Language Dictionary
  (potawatomidictionary.com) — a React/JS SPA with live-session-only audio
  and click-gated content. Use when: extracting dictionary entries, leaf nodes,
  audio MP3s, sentence examples, or bibliographic provenance from this site or
  similarly structured Indigenous language dictionaries. Combines Lightpanda
  (CDP-based headless browser) with ChromeDriver fallback. Triggers for:
  "scrape potawatomi", "download dictionary audio", "provenance.json",
  "SIL ELAN assets from dictionary", "click-jack MP3", "dictionary bot".
compatibility:
  required:
    - Python >= 3.10
    - selenium (ChromeDriver) OR playwright-python
    - lightpanda binary (optional, faster CDP path)
    - ffmpeg (for MP3 metadata tagging)
    - jq (for provenance JSON validation)
  optional:
    - Lightpanda binary: https://github.com/lightpanda-io/browser/releases
---

# Potawatomi Dictionary Scraper Skill

Scrapes **potawatomidictionary.com/Dictionary** — a React SPA with:
- **312 paginated pages** of dictionary entries
- **Leaf/entry nodes** expandable by click (e.g., "car [bodwéwdamget]")
- **Per-entry audio** — streamed MP3s, click-to-play, session-scoped URLs
- **Sentence examples** with paired audio
- Anti-scraping: Cloudflare, no SSR, session tokens, JS-only rendering

Output: Markdown entry files + MP3s + `provenance.json` with SHA-256 hashes.

---

## Architecture Decision

| Layer | Tool | Why |
|---|---|---|
| Browser automation | ChromeDriver (Selenium) | Reliable, widely tested, LinkedIn-Easy-Apply-Bot proven pattern |
| CDP acceleration | Lightpanda | Drop-in CDP replacement, 10x lighter than Chrome for bulk page iteration |
| Audio interception | CDP Network events | Capture signed MP3 URLs before they expire |
| Rate limiting | `scrape.csv` pattern profile | Human-paced, randomized delays, ban avoidance |
| Provenance | SHA-256 + bibliographic JSON | SIL/ELAN compliance, citation chain |

---

## File Layout

```
potawatomi-scraper/
├── skill/
│   └── SKILL.md              ← this file
├── scripts/
│   ├── bot.py                ← main ChromeDriver bot
│   ├── cdp_audio_tap.py      ← CDP network interceptor for MP3 URLs
│   ├── provenance.py         ← SHA-256 + bibliographic provenance builder
│   ├── scrape.csv            ← pattern profile (delays, user-agents, schedule)
│   └── elan_export.py        ← SIL ELAN .eaf asset builder (Phase 3)
├── references/
│   ├── anti_ban.md           ← rate limiting strategy guide
│   └── sil_elan_spec.md      ← ELAN .eaf XML spec notes
├── output/
│   ├── entries/              ← per-entry Markdown files
│   ├── audio/                ← downloaded MP3s, named by entry ID
│   └── provenance.json       ← master provenance manifest
└── README.md
```

---

## Phase 1 — Site Reconnaissance (run first)

Before bulk scraping, run `bot.py --recon` to:
1. Map the page structure (entry count, pagination pattern, leaf click targets)
2. Intercept one audio request to confirm URL pattern / session token format
3. Write `scrape.csv` with a learned pattern profile

```bash
python scripts/bot.py --recon --output recon_report.json
```

## Phase 2 — Bulk Extraction (weeks, not hours)

See `scrape.csv` for the pacing schedule. Key strategy:
- **1 page per 3–8 minutes** (randomized), human-like mouse jitter
- **Session rotation** every ~50 pages (new browser profile, new IP if proxied)
- **Resume support** via `--resume` flag — reads completed page IDs from provenance.json
- **CDP audio tap** active during all page visits — captures MP3 URLs as they load

```bash
python scripts/bot.py \
  --pages 1-312 \
  --profile scrape.csv \
  --output output/ \
  --resume
```

## Phase 3 — SIL ELAN Export (post-collection)

Once audio + transcriptions are collected:
```bash
python scripts/elan_export.py \
  --entries output/entries/ \
  --audio output/audio/ \
  --provenance output/provenance.json \
  --out output/elan/
```

---

## Provenance Schema

Each entry in `provenance.json`:

```json
{
  "entry_id": "bodwéwdamget_car",
  "source_url": "https://www.potawatomidictionary.com/Dictionary?page=14",
  "page": 14,
  "scraped_at": "2026-04-20T12:34:56Z",
  "scraper_version": "1.0.0",
  "html_sha256": "e3b0c44298fc1c149afb...",
  "audio": [
    {
      "type": "word",
      "filename": "bodwéwdamget_word.mp3",
      "sha256": "a87ff679a2f3e71d9181...",
      "source_url": "https://cdn.potawatomidictionary.com/audio/...",
      "duration_s": 1.4
    },
    {
      "type": "sentence",
      "filename": "bodwéwdamget_sentence_01.mp3",
      "sha256": "eccbc87e4b5ce2fe2836...",
      "source_url": "https://cdn.potawatomidictionary.com/audio/...",
      "duration_s": 4.2
    }
  ],
  "bibliographic": {
    "title": "Potawatomi Language Dictionary",
    "publisher": "Citizen Potawatomi Nation",
    "url": "https://www.potawatomidictionary.com",
    "access_date": "2026-04-20",
    "license_note": "Contact CPN Language Department for reuse terms"
  }
}
```

---

## Key Notes

- **Never automate logins** or bypass authentication — only public-facing pages
- **Respect robots.txt** — check before each session
- **Store raw HTML** per page alongside Markdown — provenance requires it
- **MP3 URLs are session-scoped** — must be downloaded in same browser session as interception
- **Do not hotlink** — download and store locally, cite source in provenance
- See `references/anti_ban.md` for proxy rotation and header spoofing guidance
