#!/usr/bin/env python3
"""
algic_server.py — Algic Family Etymology Comparator & Format Pipeline
======================================================================
Distilled from the Arcee/Trinity session, reorganised into one clean server.

What this replaces (the "brick"):
  AlgicApp, AlgicTranslator, AlgonquianEtymology, CentralAlgonquianCognates,
  CrossLinguisticMapper, EnhancedCrossLinguisticMapper, LinguisticExporter,
  AlgicRAGSystem, MultilingualAlgicRAG, OLACParser, PALAClient,
  PALAIntegratedMapper, XMLToSQLite … (50+ duplicated classes)

Architecture: one FastAPI server, modular routes, single SQLite DB.

Routes:
  GET  /                          → status
  GET  /languages                 → ALGIC_LANGUAGES table
  POST /ingest/olac               → harvest OAI-PMH, store to DB
  POST /ingest/pala               → scrape Proto-Algonquian atlas
  POST /ingest/url                → generic page scrape → DB
  GET  /cognates?word=nipi&lang=mia  → cognate set across family
  GET  /etymology?word=nipi&lang=mia → proto-form + descendants
  GET  /compare?w1=nipi&l1=mia&w2=nipiy&l2=cre → pairwise comparison
  GET  /search?q=water&langs=mia,kic,pot → cross-language search
  POST /export/tmx                → TMX 1.4 download
  POST /export/xliff              → XLIFF 2.0 download
  POST /export/lift               → LIFT 0.13 download
  POST /export/eaf                → EAF 2.8 download
  POST /export/tei                → TEI P5 download
  POST /export/dmlex              → DMLex (OASIS 2023) download
  POST /rag/query                 → Ollama RAG query over corpus
  GET  /rag/context?word=nipi     → retrieval context for a word

Install:
  pip install fastapi uvicorn requests beautifulsoup4 sqlite-vec --break-system-packages
  # Ollama must be running: ollama serve

Run:
  python3 algic_server.py
  python3 algic_server.py --port 8080 --db myaamia.db --ollama http://localhost:11434
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
import struct
import time
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import uvicorn
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Language registry
# ---------------------------------------------------------------------------
ALGIC_LANGUAGES: Dict[str, Dict[str, Any]] = {
    # Plains
    "bft": {"name": "Blackfoot",        "branch": "Plains"},
    "arp": {"name": "Arapaho",          "branch": "Plains"},
    "ats": {"name": "Gros Ventre",      "branch": "Plains"},
    "chy": {"name": "Cheyenne",         "branch": "Plains"},
    # Central — core focus
    "mia": {"name": "Miami-Illinois",   "branch": "Central", "priority": True},
    "kic": {"name": "Kickapoo",         "branch": "Central", "priority": True},
    "pot": {"name": "Potawatomi",       "branch": "Central", "priority": True},
    "sac": {"name": "Meskwaki (Fox)",   "branch": "Central", "priority": True},
    "sha": {"name": "Shawnee",          "branch": "Central"},
    "men": {"name": "Menominee",        "branch": "Central"},
    "cre": {"name": "Cree",             "branch": "Central"},
    "csw": {"name": "Swampy Cree",      "branch": "Central"},
    "pot": {"name": "Potawatomi",       "branch": "Central"},
    "oji": {"name": "Ojibwe",           "branch": "Central"},
    "otw": {"name": "Ottawa",           "branch": "Central"},
    "ciw": {"name": "Chippewa",         "branch": "Central"},
    # Eastern
    "mic": {"name": "Mi'kmaq",          "branch": "Eastern"},
    "abe": {"name": "Western Abenaki",  "branch": "Eastern"},
    "moh": {"name": "Mohegan-Pequot",   "branch": "Eastern"},
    # Proto / reconstructed
    "alg": {"name": "Proto-Algonquian", "branch": "Proto",   "reconstructed": True},
    # Kickapoo Spanish-side variety tag
    "kic-mx": {"name": "Kickapoo (Mexico)", "branch": "Central", "variety": "mx"},
}

# ---------------------------------------------------------------------------
# DB bootstrap
# ---------------------------------------------------------------------------
SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS entries (
    id            TEXT PRIMARY KEY,
    lang          TEXT NOT NULL,
    form          TEXT NOT NULL,
    ipa           TEXT,
    pos           TEXT,
    gloss_en      TEXT,
    gloss_fr      TEXT,       -- for Miami-Illinois French archive records
    gloss_es      TEXT,       -- for Kickapoo Mexico-side records
    proto_form    TEXT,       -- *PA reconstruction
    source_url    TEXT,
    source_type   TEXT,       -- olac | pala | dict | manual
    confidence    REAL DEFAULT 0.5,
    media_urls    TEXT,       -- JSON array of audio/video URLs
    created_at    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cognate_sets (
    id         TEXT PRIMARY KEY,
    proto_form TEXT,
    notes      TEXT
);

CREATE TABLE IF NOT EXISTS cognate_members (
    set_id     TEXT REFERENCES cognate_sets(id),
    entry_id   TEXT REFERENCES entries(id),
    PRIMARY KEY (set_id, entry_id)
);

CREATE TABLE IF NOT EXISTS examples (
    id          TEXT PRIMARY KEY,
    entry_id    TEXT REFERENCES entries(id),
    sentence    TEXT,
    translation TEXT,
    lang_trans  TEXT DEFAULT 'en',
    source      TEXT
);

CREATE TABLE IF NOT EXISTS olac_records (
    id            TEXT PRIMARY KEY,
    oai_id        TEXT,
    title         TEXT,
    description   TEXT,
    lang          TEXT,
    rights        TEXT,
    raw_xml       TEXT,
    harvested_at  TEXT
);

-- embeddings: created lazily if sqlite-vec is available
-- CREATE VIRTUAL TABLE IF NOT EXISTS entry_vec USING vec0(vec FLOAT[384]);

CREATE INDEX IF NOT EXISTS idx_entries_lang ON entries(lang);
CREATE INDEX IF NOT EXISTS idx_entries_form ON entries(form);
CREATE INDEX IF NOT EXISTS idx_entries_proto ON entries(proto_form);
"""


def get_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str):
    conn = get_db(db_path)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_id(*parts: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, ":".join(parts)))


def esc(s: str) -> str:
    if not s:
        return ""
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;"))


def write_xml(content: str, filename: str, media_type: str = "application/xml") -> Response:
    return Response(
        content=content.encode("utf-8"),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class IngestOLACRequest(BaseModel):
    repos: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    max_records: int = 200

class IngestURLRequest(BaseModel):
    url: str
    lang: str
    source_type: str = "dict"

class ExportRequest(BaseModel):
    source_lang: str
    target_lang: str = "en"
    min_confidence: float = 0.3

class RAGQueryRequest(BaseModel):
    query: str
    langs: Optional[List[str]] = None
    top_k: int = 8
    model: str = "gemma3:2b"


# ---------------------------------------------------------------------------
# OLAC harvester
# ---------------------------------------------------------------------------
NS_OAI  = "http://www.openarchives.org/OAI/2.0/"
NS_DC   = "http://purl.org/dc/elements/1.1/"
NS_OAIDC = "http://www.openarchives.org/OAI/2.0/oai_dc/"

DEFAULT_REPOS = [
    "https://olac.org/repository/crdo/",
    "https://olac.org/repository/mpi/",
    "https://olac.org/repository/asu/",
    "https://olac.org/repository/uchicago/",
    "https://olac.org/repository/ailla/",
    "https://olac.org/repository/elar/",
]


def harvest_olac(repos: List[str], languages: List[str], max_records: int,
                 db_path: str) -> int:
    import xml.etree.ElementTree as ET
    saved = 0
    conn = get_db(db_path)

    for repo in repos:
        token = None
        for _ in range(20):
            params = ({"resumptionToken": token} if token else
                      {"verb": "ListRecords", "metadataPrefix": "olac"})
            try:
                resp = requests.get(repo, params=params, timeout=30)
                resp.raise_for_status()
                root = ET.fromstring(resp.content)
            except Exception as e:
                print(f"OLAC harvest error {repo}: {e}")
                break

            for rec in root.findall(f".//{{{NS_OAI}}}record"):
                hdr = rec.find(f"{{{NS_OAI}}}header")
                if hdr is None:
                    continue
                id_el = hdr.find(f"{{{NS_OAI}}}identifier")
                if id_el is None or not id_el.text:
                    continue
                oai_id = id_el.text.strip()

                meta = rec.find(f"{{{NS_OAI}}}metadata")
                if meta is None:
                    continue
                dc = (meta.find(f"{{{NS_OAIDC}}}dc") or
                      meta.find(f"{{{{{NS_OAI}}}}}dc") or meta)

                def dcf(tag):
                    el = dc.find(f"{{{NS_DC}}}{tag}")
                    return (el.text or "").strip() if el is not None else ""

                lang_text = dcf("language")
                lang_code = _best_code(lang_text, languages)
                if lang_code not in languages:
                    continue

                rec_id = make_id(oai_id)
                try:
                    conn.execute("""
                        INSERT OR IGNORE INTO olac_records
                        (id,oai_id,title,description,lang,rights,raw_xml,harvested_at)
                        VALUES (?,?,?,?,?,?,?,?)
                    """, (rec_id, oai_id, dcf("title"), dcf("description"),
                          lang_code, dcf("rights"),
                          ET.tostring(dc, encoding="unicode"),
                          datetime.utcnow().isoformat()))
                    conn.commit()
                    saved += 1
                except Exception:
                    pass

                if saved >= max_records:
                    break

            tok_el = root.find(f".//{{{NS_OAI}}}resumptionToken")
            token = tok_el.text if tok_el is not None and tok_el.text else None
            if not token or saved >= max_records:
                break
            time.sleep(1)

    conn.close()
    return saved


def _best_code(lang_text: str, allowed: List[str]) -> str:
    for m in re.finditer(r'\b([a-z]{3})\b', lang_text.lower()):
        if m.group(1) in allowed:
            return m.group(1)
    m = re.search(r'\b([a-z]{3})\b', lang_text.lower())
    return m.group(1) if m else "und"


# ---------------------------------------------------------------------------
# Proto-Algonquian atlas scraper
# ---------------------------------------------------------------------------
def scrape_pala(db_path: str) -> int:
    """
    Scrape https://protoalgonquian.atlas-ling.ca for reconstructed PA forms
    and their Algonquian daughter cognates.
    """
    base = "https://protoalgonquian.atlas-ling.ca"
    saved = 0
    conn = get_db(db_path)

    try:
        resp = requests.get(base, timeout=30,
                            headers={"User-Agent": "AlgicResearchBot/1.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        conn.close()
        raise RuntimeError(f"PALA scrape error: {e}")

    # Typical PALA layout: table rows with proto-form + cognates
    for row in soup.select("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        proto = cells[0].get_text(strip=True)
        if not proto.startswith("*"):
            continue  # skip non-reconstructions

        gloss = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        proto_id = make_id("pala", proto)

        try:
            conn.execute("""
                INSERT OR IGNORE INTO entries
                (id, lang, form, gloss_en, proto_form, source_url, source_type, confidence)
                VALUES (?,?,?,?,?,?,?,?)
            """, (proto_id, "alg", proto, gloss, proto, base, "pala", 0.9))
            conn.commit()
            saved += 1
        except Exception:
            pass

        # Daughter forms in subsequent cells
        for cell in cells[2:]:
            text = cell.get_text(strip=True)
            if not text:
                continue
            # Try to extract lang tag e.g. "mia: nipiy"
            m = re.match(r'([a-z]{2,4})[:\s]+(.+)', text)
            if m:
                lang, form = m.group(1), m.group(2).strip()
            else:
                lang, form = "und", text

            entry_id = make_id("pala-daughter", proto, lang, form)
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO entries
                    (id, lang, form, gloss_en, proto_form, source_url, source_type, confidence)
                    VALUES (?,?,?,?,?,?,?,?)
                """, (entry_id, lang, form, gloss, proto, base, "pala", 0.75))
                # Link into cognate set
                set_id = make_id("cogset", proto)
                conn.execute("INSERT OR IGNORE INTO cognate_sets(id,proto_form) VALUES(?,?)",
                             (set_id, proto))
                conn.execute("INSERT OR IGNORE INTO cognate_members(set_id,entry_id) VALUES(?,?)",
                             (set_id, entry_id))
                conn.commit()
                saved += 1
            except Exception:
                pass

    conn.close()
    return saved


# ---------------------------------------------------------------------------
# Generic URL scraper (dictionaries, sites)
# ---------------------------------------------------------------------------
def scrape_url(url: str, lang: str, source_type: str, db_path: str) -> int:
    conn = get_db(db_path)
    saved = 0
    try:
        resp = requests.get(url, timeout=30,
                            headers={"User-Agent": "AlgicResearchBot/1.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        conn.close()
        raise RuntimeError(f"Scrape error {url}: {e}")

    import json

    # Generic heuristic: look for definition-list / table patterns
    for item in soup.select("dt,td,li"):
        text = item.get_text(strip=True)
        if not text or len(text) < 2:
            continue

        # Patterns like  "nipi — water" or "nipi: water"
        m = re.match(r'^([^\—\:\-]+)[—:\-]+(.+)$', text)
        if m:
            form = m.group(1).strip()
            gloss = m.group(2).strip()
        else:
            form, gloss = text, ""

        if len(form) > 80:
            continue  # likely prose, not a headword

        # Detect media links on the same page
        media = []
        parent = item.find_parent()
        if parent:
            for a in parent.find_all("a", href=True):
                href = a["href"]
                if re.search(r'\.(mp3|mp4|wav|ogg|m4a)$', href, re.I):
                    media.append(href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/"))
            for a in parent.find_all("a", href=True):
                if "youtube.com" in a["href"] or "youtu.be" in a["href"]:
                    media.append(a["href"])

        entry_id = make_id(url, lang, form)
        try:
            conn.execute("""
                INSERT OR IGNORE INTO entries
                (id, lang, form, gloss_en, source_url, source_type, confidence, media_urls)
                VALUES (?,?,?,?,?,?,?,?)
            """, (entry_id, lang, form, gloss, url, source_type, 0.5,
                  json.dumps(media) if media else None))
            conn.commit()
            saved += 1
        except Exception:
            pass

    conn.close()
    return saved


# ---------------------------------------------------------------------------
# Etymology / cognate queries
# ---------------------------------------------------------------------------
def get_cognates(word: str, lang: str, db_path: str) -> List[Dict]:
    conn = get_db(db_path)
    # Find the entry
    rows = conn.execute("""
        SELECT e.id, e.form, e.lang, e.gloss_en, e.proto_form
        FROM entries e
        WHERE e.lang=? AND (e.form=? OR e.form LIKE ?)
        LIMIT 5
    """, (lang, word, f"{word}%")).fetchall()

    if not rows:
        conn.close()
        return []

    results = []
    for row in rows:
        entry_id = row["id"]
        proto    = row["proto_form"]

        # Find cognate set
        sets = conn.execute("""
            SELECT cm.set_id FROM cognate_members cm WHERE cm.entry_id=?
        """, (entry_id,)).fetchall()

        cognates = []
        for s in sets:
            members = conn.execute("""
                SELECT e2.lang, e2.form, e2.gloss_en, e2.ipa
                FROM cognate_members cm2
                JOIN entries e2 ON cm2.entry_id = e2.id
                WHERE cm2.set_id=? AND e2.id != ?
            """, (s["set_id"], entry_id)).fetchall()
            cognates.extend([dict(r) for r in members])

        # Also find by shared proto_form
        if proto:
            by_proto = conn.execute("""
                SELECT lang, form, gloss_en, ipa
                FROM entries
                WHERE proto_form=? AND id != ?
                LIMIT 20
            """, (proto, entry_id)).fetchall()
            cognates.extend([dict(r) for r in by_proto])

        # Dedupe
        seen = set()
        deduped = []
        for c in cognates:
            key = (c["lang"], c["form"])
            if key not in seen:
                seen.add(key)
                deduped.append(c)

        results.append({
            "query_form":  row["form"],
            "query_lang":  row["lang"],
            "gloss":       row["gloss_en"],
            "proto_form":  proto,
            "cognates":    deduped,
        })

    conn.close()
    return results


def compare_pair(w1: str, l1: str, w2: str, l2: str, db_path: str) -> Dict:
    """Pairwise phonological/etymological comparison."""
    def fetch(w, l):
        conn = get_db(db_path)
        r = conn.execute(
            "SELECT * FROM entries WHERE lang=? AND form=? LIMIT 1", (l, w)
        ).fetchone()
        conn.close()
        return dict(r) if r else None

    e1 = fetch(w1, l1)
    e2 = fetch(w2, l2)

    # Simple phonological similarity (edit distance / shared phones)
    def lev(a, b):
        if not a: return len(b)
        if not b: return len(a)
        dp = list(range(len(b)+1))
        for i, ca in enumerate(a):
            ndp = [i+1]
            for j, cb in enumerate(b):
                ndp.append(min(dp[j]+(ca!=cb), dp[j+1]+1, ndp[-1]+1))
            dp = ndp
        return dp[-1]

    sim = None
    if e1 and e2:
        dist = lev(w1.lower(), w2.lower())
        maxl = max(len(w1), len(w2))
        sim  = round(1 - dist/maxl, 3) if maxl else 1.0

    # Shared proto-form?
    shared_proto = None
    if e1 and e2 and e1.get("proto_form") and e1["proto_form"] == e2.get("proto_form"):
        shared_proto = e1["proto_form"]

    return {
        "word1": {"form": w1, "lang": l1, "entry": e1},
        "word2": {"form": w2, "lang": l2, "entry": e2},
        "phonological_similarity": sim,
        "shared_proto_form": shared_proto,
        "likely_cognates": (shared_proto is not None) or (sim is not None and sim > 0.7),
    }


def cross_search(query: str, langs: List[str], db_path: str) -> List[Dict]:
    conn = get_db(db_path)
    placeholders = ",".join("?" * len(langs))
    rows = conn.execute(f"""
        SELECT lang, form, ipa, gloss_en, gloss_fr, gloss_es, proto_form,
               source_url, confidence
        FROM entries
        WHERE (form LIKE ? OR gloss_en LIKE ?)
          AND lang IN ({placeholders})
        ORDER BY confidence DESC
        LIMIT 100
    """, [f"%{query}%", f"%{query}%"] + langs).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# RAG via Ollama
# ---------------------------------------------------------------------------
def rag_context(word: str, db_path: str, top_k: int = 8) -> List[Dict]:
    conn = get_db(db_path)
    rows = conn.execute("""
        SELECT lang, form, ipa, gloss_en, proto_form, source_url
        FROM entries
        WHERE form LIKE ? OR gloss_en LIKE ?
        ORDER BY confidence DESC
        LIMIT ?
    """, [f"%{word}%", f"%{word}%", top_k]).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def rag_query(query: str, langs: Optional[List[str]], top_k: int,
              model: str, ollama_url: str, db_path: str) -> str:
    # Retrieve context
    results = cross_search(query, langs or list(ALGIC_LANGUAGES.keys()), db_path)[:top_k]
    if not results:
        results = rag_context(query, db_path, top_k)

    ctx_lines = []
    for r in results:
        lang_name = ALGIC_LANGUAGES.get(r["lang"], {}).get("name", r["lang"])
        line = f"[{lang_name} ({r['lang']})] {r['form']}"
        if r.get("ipa"):   line += f" /{r['ipa']}/"
        if r.get("gloss_en"): line += f" = {r['gloss_en']}"
        if r.get("proto_form"): line += f" (PA: {r['proto_form']})"
        ctx_lines.append(line)

    context = "\n".join(ctx_lines) if ctx_lines else "No corpus matches found."

    prompt = f"""You are a specialist in Algonquian historical linguistics and etymology.
Use the following corpus data to answer the question. Focus on etymology, cognate relationships,
and Proto-Algonquian reconstructions. Flag any uncertainty clearly.

CORPUS DATA:
{context}

QUESTION: {query}

Answer:"""

    try:
        resp = requests.post(
            f"{ollama_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        return f"[Ollama error: {e}]\n\nContext retrieved:\n{context}"


# ---------------------------------------------------------------------------
# Export formats
# ---------------------------------------------------------------------------

def export_tmx(source_lang: str, target_lang: str, min_conf: float,
               db_path: str) -> str:
    conn = get_db(db_path)
    rows = conn.execute("""
        SELECT e1.form, e1.ipa, e1.pos, e2.form, e2.ipa, e1.proto_form, e1.confidence
        FROM entries e1
        JOIN cognate_members cm1 ON e1.id = cm1.entry_id
        JOIN cognate_members cm2 ON cm1.set_id = cm2.set_id AND cm2.entry_id != cm1.entry_id
        JOIN entries e2 ON cm2.entry_id = e2.id
        WHERE e1.lang=? AND e2.lang=? AND e1.confidence>=?
        UNION
        SELECT form, ipa, pos, gloss_en, '', '', confidence
        FROM entries
        WHERE lang=? AND gloss_en IS NOT NULL AND confidence>=?
    """, (source_lang, target_lang, min_conf,
          source_lang, min_conf)).fetchall()
    conn.close()

    tus = []
    for i, r in enumerate(rows):
        src, src_ipa, pos, tgt, tgt_ipa, proto, conf = r
        props = ""
        if src_ipa: props += f'<prop type="x-ipa-src">{esc(src_ipa)}</prop>\n'
        if tgt_ipa: props += f'<prop type="x-ipa-tgt">{esc(tgt_ipa)}</prop>\n'
        if pos:     props += f'<prop type="x-pos">{esc(pos)}</prop>\n'
        if proto:   props += f'<prop type="x-proto-algonquian">{esc(proto)}</prop>\n'
        props += f'<prop type="x-confidence">{conf:.2f}</prop>\n'
        tus.append(f"""  <tu tuid="tu{i}">
    {props.strip()}
    <tuv xml:lang="{source_lang}"><seg>{esc(src)}</seg></tuv>
    <tuv xml:lang="{target_lang}"><seg>{esc(tgt)}</seg></tuv>
  </tu>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tmx SYSTEM "tmx14.dtd">
<tmx version="1.4">
  <header creationtool="algic-server" creationtoolversion="2.0"
          datatype="PlainText" segtype="term"
          adminlang="en" srclang="{source_lang}"
          creationdate="{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"/>
  <body>
{chr(10).join(tus)}
  </body>
</tmx>
"""


def export_xliff(source_lang: str, target_lang: str, min_conf: float,
                 db_path: str) -> str:
    conn = get_db(db_path)
    rows = conn.execute("""
        SELECT form, ipa, pos, gloss_en, proto_form, confidence
        FROM entries WHERE lang=? AND confidence>=?
    """, (source_lang, min_conf)).fetchall()
    conn.close()

    units = []
    for i, r in enumerate(rows):
        form, ipa, pos, gloss, proto, conf = r
        notes = ""
        if ipa:   notes += f'<note category="ipa">{esc(ipa)}</note>\n'
        if pos:   notes += f'<note category="pos">{esc(pos)}</note>\n'
        if proto: notes += f'<note category="proto-algonquian">{esc(proto)}</note>\n'
        notes += f'<note category="confidence">{conf:.2f}</note>\n'
        state = "final" if conf >= 0.8 else "translated"
        units.append(f"""  <unit id="u{i}">
    <notes>{notes.strip()}</notes>
    <segment state="{state}">
      <source>{esc(form)}</source>
      <target>{esc(gloss or '')}</target>
    </segment>
  </unit>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0"
       version="2.0" srcLang="{source_lang}" trgLang="{target_lang}">
  <file id="f1" original="algic-corpus">
{chr(10).join(units)}
  </file>
</xliff>
"""


def export_lift(lang: str, min_conf: float, db_path: str) -> str:
    conn = get_db(db_path)
    rows = conn.execute("""
        SELECT e.id, e.form, e.ipa, e.pos, e.gloss_en, e.gloss_fr, e.gloss_es,
               e.proto_form,
               GROUP_CONCAT(ex.sentence,'|||'),
               GROUP_CONCAT(ex.translation,'|||')
        FROM entries e
        LEFT JOIN examples ex ON ex.entry_id = e.id
        WHERE e.lang=? AND e.confidence>=?
        GROUP BY e.id
    """, (lang, min_conf)).fetchall()
    conn.close()

    entries = []
    for r in rows:
        eid, form, ipa, pos, g_en, g_fr, g_es, proto, sents_raw, trans_raw = r
        if not form:
            continue
        lx_id = f"lx_{eid[:8]}"

        ipa_el  = f'<pronunciation><form lang="{lang}-fonipa"><text>{esc(ipa)}</text></form></pronunciation>' if ipa else ""
        pos_el  = f'<grammatical-info value="{esc(pos)}"/>' if pos else ""
        proto_el = f'<note type="proto-algonquian">{esc(proto)}</note>' if proto else ""

        glosses = ""
        if g_en: glosses += f'<gloss lang="en"><text>{esc(g_en)}</text></gloss>\n'
        if g_fr: glosses += f'<gloss lang="fr"><text>{esc(g_fr)}</text></gloss>\n'
        if g_es: glosses += f'<gloss lang="es"><text>{esc(g_es)}</text></gloss>\n'

        ex_els = ""
        if sents_raw:
            for sent, tr in zip(sents_raw.split("|||"), (trans_raw or "").split("|||")):
                ex_els += (f'<example><form lang="{lang}"><text>{esc(sent.strip())}</text></form>'
                           f'<translation type="Free translation">'
                           f'<form lang="en"><text>{esc(tr.strip())}</text></form>'
                           f'</translation></example>\n')

        entries.append(f"""<entry id="{lx_id}" dateCreated="{datetime.utcnow().date()}">
  <lexical-unit><form lang="{lang}"><text>{esc(form)}</text></form></lexical-unit>
  {ipa_el}
  <sense id="{lx_id}_s1">
    {pos_el}{glosses.strip()}
    <definition><form lang="en"><text>{esc(g_en or '')}</text></form></definition>
    {proto_el}
    {ex_els.strip()}
  </sense>
</entry>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<lift version="0.13" producer="algic-server 2.0">
  <header><ranges/><fields/></header>
  {"".join(entries)}
</lift>
"""


def export_eaf(lang: str, db_path: str) -> str:
    conn = get_db(db_path)
    rows = conn.execute("""
        SELECT id, form, gloss_en FROM entries WHERE lang=? LIMIT 500
    """, (lang,)).fetchall()
    conn.close()

    slots, utterances, translations = [], [], []
    for i, r in enumerate(rows):
        eid, form, gloss = r["id"][:12], r["form"], r["gloss_en"] or ""
        t0, t1 = i * 2000, i * 2000 + 1800
        slots += [
            f'<TIME_SLOT TIME_SLOT_ID="ts_{eid}_s" TIME_VALUE="{t0}"/>',
            f'<TIME_SLOT TIME_SLOT_ID="ts_{eid}_e" TIME_VALUE="{t1}"/>',
        ]
        utterances.append(f"""<ANNOTATION>
  <ALIGNABLE_ANNOTATION ANNOTATION_ID="a_{eid}"
    TIME_SLOT_REF1="ts_{eid}_s" TIME_SLOT_REF2="ts_{eid}_e">
    <ANNOTATION_VALUE>{esc(form)}</ANNOTATION_VALUE>
  </ALIGNABLE_ANNOTATION>
</ANNOTATION>""")
        translations.append(f"""<ANNOTATION>
  <REF_ANNOTATION ANNOTATION_ID="tr_{eid}" ANNOTATION_REF="a_{eid}">
    <ANNOTATION_VALUE>{esc(gloss)}</ANNOTATION_VALUE>
  </REF_ANNOTATION>
</ANNOTATION>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ANNOTATION_DOCUMENT AUTHOR="algic-server"
  DATE="{datetime.utcnow().isoformat()}" FORMAT="2.8" VERSION="2.8"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:noNamespaceSchemaLocation="http://www.mpi.nl/tools/elan/EAFv2.8.xsd">
  <HEADER MEDIA_FILE="" TIME_UNITS="milliseconds"/>
  <TIME_ORDER>{"".join(slots)}</TIME_ORDER>
  <TIER LINGUISTIC_TYPE_REF="utterance" TIER_ID="utterance@lexicon"
        DEFAULT_LOCALE="{lang}">
    {"".join(utterances)}
  </TIER>
  <TIER LINGUISTIC_TYPE_REF="translation" TIER_ID="translation@lexicon"
        PARENT_REF="utterance@lexicon" DEFAULT_LOCALE="en">
    {"".join(translations)}
  </TIER>
  <LINGUISTIC_TYPE GRAPHIC_REFERENCES="false"
    LINGUISTIC_TYPE_ID="utterance" TIME_ALIGNABLE="true"/>
  <LINGUISTIC_TYPE CONSTRAINTS="Symbolic_Association"
    GRAPHIC_REFERENCES="false"
    LINGUISTIC_TYPE_ID="translation" TIME_ALIGNABLE="false"/>
  <LOCALE LANGUAGE_CODE="{lang}"/>
  <LOCALE LANGUAGE_CODE="en"/>
</ANNOTATION_DOCUMENT>
"""


def export_tei(lang: str, min_conf: float, db_path: str) -> str:
    """TEI P5 <entry> elements in a <body>."""
    conn = get_db(db_path)
    rows = conn.execute("""
        SELECT form, ipa, pos, gloss_en, proto_form, confidence
        FROM entries WHERE lang=? AND confidence>=?
    """, (lang, min_conf)).fetchall()
    conn.close()

    lang_name = ALGIC_LANGUAGES.get(lang, {}).get("name", lang)
    entries = []
    for i, r in enumerate(rows):
        form, ipa, pos, gloss, proto, conf = r
        ipa_el   = f'<pron notation="ipa">{esc(ipa)}</pron>' if ipa else ""
        pos_el   = f'<pos><gram type="pos">{esc(pos)}</gram></pos>' if pos else ""
        proto_el = f'<etym type="proto-algonquian"><mentioned>{esc(proto)}</mentioned></etym>' if proto else ""
        entries.append(f"""  <entry xml:id="e{i}" xml:lang="{lang}">
    <form type="lemma"><orth>{esc(form)}</orth>{ipa_el}</form>
    <gramGrp>{pos_el}</gramGrp>
    <sense><def>{esc(gloss or '')}</def></sense>
    {proto_el}
  </entry>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt><title>{lang_name} Lexicon</title></titleStmt>
      <publicationStmt><p>algic-server export — {datetime.utcnow().date()}</p></publicationStmt>
      <sourceDesc><p>Derived from OLAC / PALA corpus</p></sourceDesc>
    </fileDesc>
    <profileDesc>
      <langUsage>
        <language ident="{lang}">{lang_name}</language>
        <language ident="en">English</language>
      </langUsage>
    </profileDesc>
  </teiHeader>
  <text><body>
    <div type="dictionary">
{"".join(entries)}
    </div>
  </body></text>
</TEI>
"""


def export_dmlex(lang: str, min_conf: float, db_path: str) -> str:
    """DMLex (OASIS 2023) XML serialisation."""
    conn = get_db(db_path)
    rows = conn.execute("""
        SELECT form, ipa, pos, gloss_en, proto_form, confidence
        FROM entries WHERE lang=? AND confidence>=?
    """, (lang, min_conf)).fetchall()
    conn.close()

    lang_name = ALGIC_LANGUAGES.get(lang, {}).get("name", lang)
    entries = []
    for i, r in enumerate(rows):
        form, ipa, pos, gloss, proto, conf = r
        pron_el  = f'<pronunciation><transcription scheme="IPA">{esc(ipa)}</transcription></pronunciation>' if ipa else ""
        pos_el   = f'<partOfSpeech tag="{esc(pos)}"/>' if pos else ""
        proto_el = f'<etymon><note>Proto-Algonquian: {esc(proto)}</note></etymon>' if proto else ""
        entries.append(f"""  <entry id="e{i}">
    <headword>{esc(form)}</headword>
    {pron_el}
    {pos_el}
    <sense id="e{i}_s1">
      <definition><text>{esc(gloss or '')}</text></definition>
      {proto_el}
    </sense>
  </entry>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<lexicographicResource xmlns="http://docs.oasis-open.org/lexidma/dmlex/v1.0"
                       id="{lang}-lexicon"
                       langCode="{lang}"
                       title="{lang_name} Lexicon">
  <entry><!-- generated {datetime.utcnow().date()} by algic-server --></entry>
{"".join(entries)}
</lexicographicResource>
"""


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
def build_app(db_path: str, ollama_url: str) -> FastAPI:
    app = FastAPI(
        title="Algic Etymology Comparator",
        description="Central Algonquian corpus server — mia / kic / pot / sac / sha and family",
        version="2.0",
    )

    @app.get("/")
    def root():
        conn = get_db(db_path)
        count = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        langs = conn.execute(
            "SELECT lang, COUNT(*) as n FROM entries GROUP BY lang ORDER BY n DESC"
        ).fetchall()
        conn.close()
        return {
            "status": "ok",
            "total_entries": count,
            "by_language": [{"lang": r[0], "count": r[1]} for r in langs],
        }

    @app.get("/languages")
    def languages():
        return ALGIC_LANGUAGES

    # --- Ingest ---

    @app.post("/ingest/olac")
    def ingest_olac(req: IngestOLACRequest):
        repos = req.repos or DEFAULT_REPOS
        langs = req.languages or [k for k, v in ALGIC_LANGUAGES.items()
                                   if not v.get("reconstructed")]
        n = harvest_olac(repos, langs, req.max_records, db_path)
        return {"harvested": n}

    @app.post("/ingest/pala")
    def ingest_pala():
        n = scrape_pala(db_path)
        return {"scraped": n}

    @app.post("/ingest/url")
    def ingest_url(req: IngestURLRequest):
        n = scrape_url(req.url, req.lang, req.source_type, db_path)
        return {"scraped": n, "lang": req.lang}

    # --- Query ---

    @app.get("/cognates")
    def cognates(word: str = Query(...), lang: str = Query(...)):
        return get_cognates(word, lang, db_path)

    @app.get("/etymology")
    def etymology(word: str = Query(...), lang: str = Query(...)):
        results = get_cognates(word, lang, db_path)
        if not results:
            raise HTTPException(404, f"No entry for '{word}' in {lang}")
        return results[0]

    @app.get("/compare")
    def compare(w1: str = Query(...), l1: str = Query(...),
                w2: str = Query(...), l2: str = Query(...)):
        return compare_pair(w1, l1, w2, l2, db_path)

    @app.get("/search")
    def search(q: str = Query(...),
               langs: str = Query(default=",".join(
                   k for k, v in ALGIC_LANGUAGES.items()
                   if v.get("priority") and not v.get("reconstructed")
               ))):
        lang_list = [l.strip() for l in langs.split(",") if l.strip()]
        return cross_search(q, lang_list, db_path)

    # --- RAG ---

    @app.get("/rag/context")
    def rag_ctx(word: str = Query(...), top_k: int = 8):
        return rag_context(word, db_path, top_k)

    @app.post("/rag/query")
    def rag_qry(req: RAGQueryRequest):
        answer = rag_query(
            req.query, req.langs, req.top_k, req.model, ollama_url, db_path
        )
        return {"query": req.query, "answer": answer}

    # --- Exports ---

    @app.post("/export/tmx")
    def exp_tmx(req: ExportRequest):
        xml = export_tmx(req.source_lang, req.target_lang, req.min_confidence, db_path)
        return write_xml(xml, f"{req.source_lang}-{req.target_lang}.tmx")

    @app.post("/export/xliff")
    def exp_xliff(req: ExportRequest):
        xml = export_xliff(req.source_lang, req.target_lang, req.min_confidence, db_path)
        return write_xml(xml, f"{req.source_lang}-{req.target_lang}.xliff")

    @app.post("/export/lift")
    def exp_lift(req: ExportRequest):
        xml = export_lift(req.source_lang, req.min_confidence, db_path)
        return write_xml(xml, f"{req.source_lang}.lift")

    @app.post("/export/eaf")
    def exp_eaf(req: ExportRequest):
        xml = export_eaf(req.source_lang, db_path)
        return write_xml(xml, f"{req.source_lang}.eaf")

    @app.post("/export/tei")
    def exp_tei(req: ExportRequest):
        xml = export_tei(req.source_lang, req.min_confidence, db_path)
        return write_xml(xml, f"{req.source_lang}-tei.xml")

    @app.post("/export/dmlex")
    def exp_dmlex(req: ExportRequest):
        xml = export_dmlex(req.source_lang, req.min_confidence, db_path)
        return write_xml(xml, f"{req.source_lang}-dmlex.xml")

    return app


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Algic Etymology Comparator Server")
    parser.add_argument("--db",     default="myaamia-corpus.db")
    parser.add_argument("--port",   type=int, default=8000)
    parser.add_argument("--host",   default="0.0.0.0")
    parser.add_argument("--ollama", default="http://localhost:11434")
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    init_db(args.db)
    print(f"✅  DB initialised: {args.db}")
    print(f"🌐  Docs: http://{args.host}:{args.port}/docs")

    app = build_app(args.db, args.ollama)
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)
