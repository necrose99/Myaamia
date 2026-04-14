#!/usr/bin/env python3
"""
algic_ety_applet_v3.py — Algic Etymology Applet
=================================================
Full-stack Flask server for the Algonquian language corpus.

Features
--------
• Admin / user role system  (admin: full ingest + export; user: search + permitted export)
• Saxon XSLT 2.0 round-trip (the actual sheets from xslt-linguistics-suite-final.zip)
  — lift↔tmx, lift↔xliff, eaf↔tmx, eaf↔xliff, eaf↔lift, eaf↔tei, tmx↔xliff
• translate-toolkit bridge  (LIFT → PO → TMX|XLIFF|TBX|CSV)
• TMX import / incremental update  (POST /admin/import/tmx)
• LIFT import                       (POST /admin/import/lift)
• OLAC OAI-PMH harvest + schema refs (POST /admin/import/olac)
• Wiktionary Proto-Algonquian spider (POST /admin/import/wiktionary)
• tmx_to_ollama_jsonl export        (POST /admin/export/ollama-jsonl)
• pyglossary export (StarDict, SQLite, JSON, CSV)
• JS phoneme tooltip overlay:
    – Cree syllabics (SRO)         from existing transliterator map
    – Kickapoo Roman (Voorhis/SIL)
    – Miami-Illinois Myaamia Roman (Leonard/Costa)
    – Shared Algonquian conventions
• Parchment + Native American theme

Install
-------
  pip install flask ety pyglossary saxonche lxml requests \
              beautifulsoup4 --break-system-packages
  apt install translate-toolkit python3-translate

  # Put XSLT sheets somewhere accessible, default: ./xslt/
  # (copy from xslt-linguistics-suite-final.zip linguistics-suite/xslt/)

Run
---
  python3 algic_ety_applet_v3.py [--db myaamia-corpus.db] \
          [--xslt ./xslt] [--port 5000] [--admin-key secret]
"""
from __future__ import annotations
import argparse, json, os, re, secrets, sqlite3, struct, tempfile, uuid, zipfile
from datetime import datetime
from functools import wraps
from io import BytesIO, StringIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sqlite3
import sqlite_zstd
import ety as ety_lib
import requests
from bs4 import BeautifulSoup
from flask import (Flask, Response, g, jsonify, render_template_string,
                   request, send_file, session)

# ── Language registry ────────────────────────────────────────────────────────
ALGIC: Dict[str, Dict] = {
    "mia": {"name": "Miami-Illinois",    "branch": "Central", "script": "roman",    "priority": True},
    "kic": {"name": "Kickapoo",          "branch": "Central", "script": "roman",    "priority": True},
    "pot": {"name": "Potawatomi",        "branch": "Central", "script": "roman",    "priority": True},
    "sac": {"name": "Meskwaki (Fox)",    "branch": "Central", "script": "roman",    "priority": True},
    "sha": {"name": "Shawnee",           "branch": "Central", "script": "roman"},
    "men": {"name": "Menominee",         "branch": "Central", "script": "roman"},
    "oji": {"name": "Ojibwe",            "branch": "Central", "script": "roman"},
    "cre": {"name": "Plains/Woods Cree", "branch": "Central", "script": "syllabics","priority": True},
    "csw": {"name": "Swampy Cree",       "branch": "Central", "script": "syllabics"},
    "mic": {"name": "Mi'kmaq",           "branch": "Eastern", "script": "roman"},
    "abe": {"name": "W. Abenaki",        "branch": "Eastern", "script": "roman"},
    "alg": {"name": "Proto-Algonquian★", "branch": "Proto",   "script": "roman"},
}

# OLAC schema locations (for import validation reference)
OLAC_SCHEMAS = {
    "olac":       "http://www.language-archives.org/OLAC/1.1/olac.xsd",
    "dc":         "http://dublincore.org/schemas/xmls/qdc/2006/01/06/dc.xsd",
    "dcterms":    "http://dublincore.org/schemas/xmls/qdc/2006/01/06/dcterms.xsd",
    "discourse":  "http://www.language-archives.org/OLAC/1.1/olac-discourse-type.xsd",
    "extension":  "http://www.language-archives.org/OLAC/1.1/olac-extension.xsd",
    "language":   "http://www.language-archives.org/OLAC/1.1/olac-language.xsd",
    "oai-id":     "http://www.openarchives.org/OAI/2.0/oai-identifier.xsd",
    "static-rep": "http://www.openarchives.org/OAI/2.0/static-repository.xsd",
}

NS_OAI  = "http://www.openarchives.org/OAI/2.0/"
NS_DC   = "http://purl.org/dc/elements/1.1/"
NS_OAIDC = "http://www.openarchives.org/OAI/2.0/oai_dc/"

# ── DB ───────────────────────────────────────────────────────────────────────
SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS users (
    id       TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    role     TEXT NOT NULL DEFAULT 'user',   -- 'admin' | 'user'
    api_key  TEXT UNIQUE,
    created  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS entries (
    id          TEXT PRIMARY KEY,
    lang        TEXT NOT NULL,
    form        TEXT NOT NULL,
    ipa         TEXT,
    pos         TEXT,
    gloss_en    TEXT,
    gloss_fr    TEXT,
    gloss_es    TEXT,
    proto_form  TEXT,
    morph_seg   TEXT,
    source_url  TEXT,
    source_type TEXT,  -- olac|tmx|lift|manual|wiktionary
    confidence  REAL   DEFAULT 0.5,
    media_urls  TEXT,
    created_at  TEXT   DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cognate_sets (
    id          TEXT PRIMARY KEY,
    proto_form  TEXT,
    proto_gloss TEXT,
    confidence  REAL DEFAULT 0.7,
    source_ref  TEXT,
    notes       TEXT
);

CREATE TABLE IF NOT EXISTS cognate_members (
    set_id   TEXT REFERENCES cognate_sets(id),
    entry_id TEXT REFERENCES entries(id),
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
    id           TEXT PRIMARY KEY,
    oai_id       TEXT,
    title        TEXT,
    description  TEXT,
    lang         TEXT,
    rights       TEXT,
    source_repo  TEXT,
    raw_xml      TEXT,
    harvested_at TEXT
);

CREATE TABLE IF NOT EXISTS import_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ts         TEXT DEFAULT (datetime('now')),
    username   TEXT,
    action     TEXT,
    source     TEXT,
    records_in INTEGER DEFAULT 0,
    records_new INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS export_permissions (
    role   TEXT,
    format TEXT,
    PRIMARY KEY (role, format)
);

CREATE INDEX IF NOT EXISTS idx_entries_lang  ON entries(lang);
CREATE INDEX IF NOT EXISTS idx_entries_form  ON entries(form);
CREATE INDEX IF NOT EXISTS idx_entries_proto ON entries(proto_form);
"""

DEFAULT_EXPORT_PERMS = [
    ("admin", "tmx"), ("admin", "xliff"), ("admin", "lift"), ("admin", "eaf"),
    ("admin", "tei"), ("admin", "stardict"), ("admin", "json"), ("admin", "csv"),
    ("admin", "sql"), ("admin", "ollama-jsonl"),
    ("user",  "tmx"), ("user", "json"), ("user", "csv"),
]

def init_db(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    for role, fmt in DEFAULT_EXPORT_PERMS:
        conn.execute("INSERT OR IGNORE INTO export_permissions VALUES(?,?)", (role, fmt))
    # Default admin account
    aid = str(uuid.uuid4())
    akey = secrets.token_hex(16)
    conn.execute("INSERT OR IGNORE INTO users(id,username,role,api_key) VALUES(?,?,?,?)",
                 (aid, "admin", "admin", akey))
    conn.commit()
    key_row = conn.execute("SELECT api_key FROM users WHERE username='admin'").fetchone()
    conn.close()
    return key_row[0] if key_row else akey


def db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# ── Auth ─────────────────────────────────────────────────────────────────────
def get_current_user(db_path: str) -> Optional[Dict]:
    key = (request.headers.get("X-API-Key") or
           request.args.get("api_key") or
           request.cookies.get("api_key"))
    if not key:
        return None
    row = db(db_path).execute(
        "SELECT * FROM users WHERE api_key=?", (key,)).fetchone()
    return dict(row) if row else None

def require_role(role: str, db_path_ref):
    def dec(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            user = get_current_user(db_path_ref())
            if not user:
                return jsonify({"error": "Unauthorised"}), 401
            if role == "admin" and user["role"] != "admin":
                return jsonify({"error": "Admin required"}), 403
            g.user = user
            return fn(*a, **kw)
        return wrapper
    return dec

# ── Saxon XSLT 2.0 engine ────────────────────────────────────────────────────
XSLT_DIRECTIONS = {
    # key             : (stylesheet_filename,   src_param,       tgt_param)
    "lift2tmx":        ("lift-to-tmx.xsl",      "source-lang",   None),
    "lift2xliff":      ("lift-to-xliff.xsl",    "source-lang",   "target-lang"),
    "tmx2lift":        ("tmx-to-lift.xsl",      "source-lang",   None),
    "tmx2xliff":       ("tmx-to-xliff.xsl",     "source-lang",   "target-lang"),
    "xliff2lift":      ("xliff-to-lift.xsl",    "source-lang",   None),
    "xliff2tmx":       ("xliff-to-tmx.xsl",     "source-lang",   "target-lang"),
    "eaf2tmx":         ("eaf-to-tmx.xsl",       "source-lang",   None),
    "eaf2xliff":       ("eaf-to-xliff.xsl",     "source-lang",   "target-lang"),
    "eaf2lift":        ("eaf-to-lift.xsl",       "source-lang",   None),
    "eaf2tei":         ("eaf-to-tei.xsl",        "source-lang",   None),
    "tmx2eaf":         ("tmx-to-eaf.xsl",        "source-lang",   None),
}

def saxon_transform(xslt_dir: str, direction: str,
                    xml_bytes: bytes, src_lang: str, tgt_lang: str = "en") -> bytes:
    if direction not in XSLT_DIRECTIONS:
        raise ValueError(f"Unknown direction: {direction}")
    sheet_file, src_param, tgt_param = XSLT_DIRECTIONS[direction]
    sheet_path = Path(xslt_dir) / sheet_file
    if not sheet_path.exists():
        raise FileNotFoundError(f"XSLT sheet not found: {sheet_path}")

    try:
        from saxonche import PySaxonProcessor
        with PySaxonProcessor(license=False) as proc:
            xslt = proc.new_xslt30_processor()
            exe  = xslt.compile_stylesheet(stylesheet_file=str(sheet_path))
            exe.set_parameter(src_param, proc.make_string_value(src_lang))
            if tgt_param:
                exe.set_parameter(tgt_param, proc.make_string_value(tgt_lang))
            # Write input to temp file (saxonche needs file path)
            with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tf:
                tf.write(xml_bytes); tf_name = tf.name
            result = exe.transform_to_string(source_file=tf_name)
            os.unlink(tf_name)
            return result.encode("utf-8") if isinstance(result, str) else result
    except ImportError:
        return _et_fallback(direction, xml_bytes, src_lang, tgt_lang)


def _esc(s): return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def _et_fallback(direction, xml_bytes, src_lang, tgt_lang):
    """Pure ElementTree fallback when saxonche unavailable."""
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_bytes)

    if direction == "lift2tmx":
        tus = []
        for entry in root.findall("entry"):
            f = entry.findtext("lexical-unit/form/text") or ""
            for sense in entry.findall("sense"):
                for gloss in sense.findall("gloss"):
                    gl = gloss.get("lang","en"); gt = gloss.findtext("text") or ""
                    proto = entry.findtext("sense/note[@type='proto-algonquian']") or ""
                    pp = f'<prop type="x-proto-algonquian">{_esc(proto)}</prop>' if proto else ""
                    tus.append(f'<tu>{pp}<tuv xml:lang="{src_lang}"><seg>{_esc(f)}</seg></tuv>'
                               f'<tuv xml:lang="{gl}"><seg>{_esc(gt)}</seg></tuv></tu>')
        return (f'<?xml version="1.0" encoding="UTF-8"?><tmx version="1.4">'
                f'<header srclang="{src_lang}"/><body>{"".join(tus)}</body></tmx>').encode()

    if direction in ("tmx2lift", "xliff2lift"):
        entries = []
        pairs = []
        if direction == "tmx2lift":
            for tu in root.iter("tu"):
                tuvs = list(tu.findall("tuv"))
                if len(tuvs) >= 2:
                    pairs.append((tuvs[0].findtext("seg") or "", tuvs[1].findtext("seg") or "",
                                  tu.get("tuid", str(uuid.uuid4())[:8])))
        else:
            for unit in root.iter("{urn:oasis:names:tc:xliff:document:1.2}trans-unit"):
                pairs.append((unit.findtext("{urn:oasis:names:tc:xliff:document:1.2}source") or "",
                               unit.findtext("{urn:oasis:names:tc:xliff:document:1.2}target") or "",
                               unit.get("id","u")))
        for src, tgt, eid in pairs:
            entries.append(f'<entry id="lx_{eid}"><lexical-unit><form lang="{src_lang}">'
                           f'<text>{_esc(src)}</text></form></lexical-unit>'
                           f'<sense id="s1"><gloss lang="{tgt_lang}">'
                           f'<text>{_esc(tgt)}</text></gloss></sense></entry>')
        return (f'<?xml version="1.0" encoding="UTF-8"?>'
                f'<lift version="0.13" producer="algic-fallback">'
                f'<header><ranges/><fields/></header>{"".join(entries)}</lift>').encode()

    raise ValueError(f"ET fallback not implemented for {direction}")


# ── translate-toolkit bridge ─────────────────────────────────────────────────
def tt_convert(lift_xml: bytes, src_lang: str, tgt_lang: str, fmt: str) -> bytes:
    import xml.etree.ElementTree as ET
    from translate.storage.pypo import pofile as POFile

    root = ET.fromstring(lift_xml)
    po = POFile(); po.setsourcelanguage(src_lang); po.settargetlanguage(tgt_lang)
    for entry in root.findall("entry"):
        f_el = entry.find("lexical-unit/form/text")
        g_el = (entry.find(f"sense/gloss[@lang='{tgt_lang}']/text") or
                entry.find(f"sense/definition/form[@lang='{tgt_lang}']/text"))
        if f_el is None: continue
        form = (f_el.text or "").strip(); gloss = (g_el.text if g_el is not None else "").strip()
        if not form: continue
        unit = po.addsourceunit(form); unit.target = gloss
        proto = entry.findtext("sense/note[@type='proto-algonquian']")
        if proto: unit.addnote(f"PA: {proto}", "developer")
        pos = entry.find("sense/grammatical-info")
        if pos is not None: unit.addnote(f"pos: {pos.get('value','')}", "developer")

    buf = BytesIO(); po.serialize(buf); po_bytes = buf.getvalue()
    if fmt == "po": return po_bytes

    def po_obj():
        from translate.storage.pypo import pofile as PF; f = PF(); f.parse(po_bytes); return f

    if fmt == "tmx":
        from translate.storage import tmx as tmxstore
        t = tmxstore.tmxfile(); t.setsourcelanguage(src_lang); t.settargetlanguage(tgt_lang)
        for u in po_obj().units:
            if not u.source: continue
            tu = t.addsourceunit(u.source); tu.settarget(u.target, tgt_lang)
        b2 = BytesIO(); t.serialize(b2); return b2.getvalue()
    if fmt == "xliff":
        from translate.storage import xliff as xliffstore
        x = xliffstore.xlifffile(); x.setsourcelanguage(src_lang); x.settargetlanguage(tgt_lang)
        for u in po_obj().units:
            if not u.source: continue
            xu = x.addsourceunit(u.source); xu.target = u.target
        b2 = BytesIO(); x.serialize(b2); return b2.getvalue()
    if fmt == "tbx":
        from translate.storage import tbx as tbxstore
        b = tbxstore.tbxfile()
        for u in po_obj().units:
            if not u.source: continue
            bu = b.addsourceunit(u.source); bu.target = u.target
        b2 = BytesIO(); b.serialize(b2); return b2.getvalue()
    if fmt == "csv":
        import csv, io as _io
        b2 = _io.StringIO(); w = csv.writer(b2); w.writerow([src_lang, tgt_lang, "notes"])
        for u in po_obj().units:
            if not u.source: continue
            w.writerow([u.source, u.target, u.getnotes() or ""])
        return b2.getvalue().encode()
    raise ValueError(f"Unknown tt format: {fmt}")


# ── TMX import / incremental update ──────────────────────────────────────────
def import_tmx(tmx_bytes: bytes, src_lang: str, db_path: str,
               username: str = "system") -> Tuple[int, int]:
    """Parse TMX, upsert entries. Returns (total_seen, new_inserted)."""
    import xml.etree.ElementTree as ET

    try:
        # Try generateDS binding first (from zip)
        import sys; sys.path.insert(0, "/tmp/linguistics-suite/bindings")
        import tmx14_ds
        root = tmx14_ds.parseString(tmx_bytes, silence=True)
        tus_raw = root.get_body().get_tu() if root.get_body() else []
        pairs = []
        for tu in tus_raw:
            tuvs = tu.get_tuv() or []
            if len(tuvs) < 2: continue
            def seg(t): return (t.get_seg() or "").strip()
            def lang(t):
                attrs = t.get_anyAttributes_() or {}
                return attrs.get("lang", attrs.get("{http://www.w3.org/XML/1998/namespace}lang","und"))
            pairs.append({
                "src": seg(tuvs[0]), "tgt": seg(tuvs[1]),
                "src_lang": lang(tuvs[0]), "tgt_lang": lang(tuvs[1]),
                "props": {p.get_type(): p.get_valueOf_() for p in (tu.get_prop() or [])}
            })
    except Exception:
        # Fallback: plain ET parse
        root_et = ET.fromstring(tmx_bytes)
        pairs = []
        for tu in root_et.iter("tu"):
            tuvs = list(tu.findall("tuv"))
            if len(tuvs) < 2: continue
            def xlang(el):
                return (el.get("{http://www.w3.org/XML/1998/namespace}lang") or
                        el.get("lang") or "und")
            props = {p.get("type"): (p.text or "").strip() for p in tu.findall("prop")}
            pairs.append({
                "src": (tuvs[0].findtext("seg") or "").strip(),
                "tgt": (tuvs[1].findtext("seg") or "").strip(),
                "src_lang": xlang(tuvs[0]), "tgt_lang": xlang(tuvs[1]),
                "props": props,
            })

    conn = db(db_path); total = len(pairs); new = 0
    for p in pairs:
        if not p["src"]: continue
        eid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{p['src_lang']}:{p['src']}"))
        existing = conn.execute("SELECT id FROM entries WHERE id=?", (eid,)).fetchone()
        if existing:
            # Update gloss if improved
            conn.execute("UPDATE entries SET gloss_en=? WHERE id=? AND (gloss_en IS NULL OR gloss_en='')",
                         (p["tgt"], eid))
        else:
            conn.execute("""INSERT OR IGNORE INTO entries
                (id,lang,form,gloss_en,proto_form,source_type,confidence)
                VALUES(?,?,?,?,?,?,?)""",
                (eid, p["src_lang"] or src_lang, p["src"], p["tgt"],
                 p["props"].get("x-proto-algonquian") or p["props"].get("x-pa"),
                 "tmx", 0.7))
            new += 1
    conn.execute("INSERT INTO import_log(username,action,source,records_in,records_new) VALUES(?,?,?,?,?)",
                 (username, "import_tmx", "tmx-upload", total, new))
    conn.commit(); conn.close()
    return total, new


def import_lift(lift_bytes: bytes, src_lang: str, db_path: str,
                username: str = "system") -> Tuple[int, int]:
    import xml.etree.ElementTree as ET
    root = ET.fromstring(lift_bytes)
    conn = db(db_path); total = 0; new = 0

    for entry in root.findall("entry"):
        f_el = entry.find(f"lexical-unit/form[@lang='{src_lang}']/text") or \
               entry.find("lexical-unit/form/text")
        if f_el is None or not f_el.text: continue
        form = f_el.text.strip(); total += 1
        eid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{src_lang}:{form}"))

        ipa = entry.findtext(f"pronunciation/form[@lang='{src_lang}-fonipa']/text") or \
              entry.findtext("pronunciation/form/text") or ""
        morph = entry.findtext("note[@type='morph-segmentation']") or ""
        proto = entry.findtext("note[@type='etym']") or \
                entry.findtext("sense/note[@type='proto-algonquian']") or ""
        # strip ** prefix from proto notation
        proto = re.sub(r'^\*+', '*', proto.split('"')[0].strip()) if proto else ""

        g_en = entry.findtext("sense/gloss[@lang='en']/text") or ""
        g_fr = entry.findtext("sense/gloss[@lang='fr']/text") or ""
        g_es = entry.findtext("sense/gloss[@lang='es']/text") or ""
        gi   = entry.find("sense/grammatical-info")
        pos  = gi.get("value", "") if gi is not None else ""

        existing = conn.execute("SELECT id FROM entries WHERE id=?", (eid,)).fetchone()
        if not existing:
            conn.execute("""INSERT OR IGNORE INTO entries
                (id,lang,form,ipa,pos,gloss_en,gloss_fr,gloss_es,proto_form,morph_seg,source_type,confidence)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (eid,src_lang,form,ipa,pos,g_en,g_fr,g_es,proto,morph,"lift",0.8))
            new += 1
        else:
            # Update richer fields if we now have them
            conn.execute("""UPDATE entries SET ipa=COALESCE(NULLIF(ipa,''),?),
                pos=COALESCE(NULLIF(pos,''),?), proto_form=COALESCE(NULLIF(proto_form,''),?)
                WHERE id=?""", (ipa, pos, proto, eid))

        # Examples
        for ex in entry.findall("sense/example"):
            sent = ex.findtext(f"form[@lang='{src_lang}']/text") or ""
            trans = ex.findtext("translation/form[@lang='en']/text") or ""
            if sent:
                exid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{eid}:{sent}"))
                conn.execute("INSERT OR IGNORE INTO examples(id,entry_id,sentence,translation) VALUES(?,?,?,?)",
                             (exid, eid, sent, trans))

    conn.execute("INSERT INTO import_log(username,action,source,records_in,records_new) VALUES(?,?,?,?,?)",
                 (username,"import_lift","lift-upload",total,new))
    conn.commit(); conn.close()
    return total, new


# ── OLAC OAI-PMH harvest ─────────────────────────────────────────────────────
DEFAULT_OLAC_REPOS = [
    "https://olac.org/repository/crdo/",
    "https://olac.org/repository/mpi/",
    "https://olac.org/repository/asu/",
    "https://olac.org/repository/ailla/",
    "https://olac.org/repository/elar/",
]

def harvest_olac(repos: List[str], languages: List[str],
                 max_records: int, db_path: str,
                 username: str = "system") -> Tuple[int, int]:
    import xml.etree.ElementTree as ET
    conn = db(db_path); total = 0; new = 0

    def dcf(el, tag):
        f = el.find(f"{{{NS_DC}}}{tag}")
        return (f.text or "").strip() if f is not None else ""

    def best_code(text):
        for m in re.finditer(r'\b([a-z]{3})\b', text.lower()):
            if m.group(1) in languages: return m.group(1)
        m = re.search(r'\b([a-z]{3})\b', text.lower())
        return m.group(1) if m else None

    for repo in repos:
        token = None
        for _ in range(15):
            params = ({"resumptionToken": token} if token else
                      {"verb": "ListRecords", "metadataPrefix": "olac"})
            try:
                resp = requests.get(repo, params=params, timeout=30)
                resp.raise_for_status()
                root = ET.fromstring(resp.content)
            except Exception as e:
                print(f"OLAC harvest error {repo}: {e}"); break

            for rec in root.findall(f".//{{{NS_OAI}}}record"):
                id_el = rec.find(f".//{{{NS_OAI}}}identifier")
                if id_el is None: continue
                oai_id = id_el.text or ""
                meta = rec.find(f"{{{NS_OAI}}}metadata")
                if meta is None: continue
                dc = (meta.find(f"{{{NS_OAIDC}}}dc") or meta)
                lang_text = dcf(dc, "language")
                lang_code = best_code(lang_text)
                if not lang_code: continue
                total += 1
                rid = str(uuid.uuid5(uuid.NAMESPACE_URL, oai_id))
                existing = conn.execute("SELECT id FROM olac_records WHERE id=?", (rid,)).fetchone()
                if not existing:
                    conn.execute("""INSERT OR IGNORE INTO olac_records
                        (id,oai_id,title,description,lang,rights,source_repo,raw_xml,harvested_at)
                        VALUES(?,?,?,?,?,?,?,?,?)""",
                        (rid, oai_id, dcf(dc,"title"), dcf(dc,"description"),
                         lang_code, dcf(dc,"rights"), repo,
                         ET.tostring(dc, encoding="unicode"),
                         datetime.utcnow().isoformat()))
                    new += 1

            tok_el = root.find(f".//{{{NS_OAI}}}resumptionToken")
            token = tok_el.text if tok_el is not None and tok_el.text else None
            if not token or total >= max_records: break
            import time; time.sleep(1)

    conn.execute("INSERT INTO import_log(username,action,source,records_in,records_new) VALUES(?,?,?,?,?)",
                 (username,"harvest_olac",",".join(repos),total,new))
    conn.commit(); conn.close()
    return total, new


# ── Wiktionary Proto-Algonquian spider ────────────────────────────────────────
def harvest_wiktionary_pa(db_path: str, max_pages: int = 200,
                          username: str = "system") -> Tuple[int, int]:
    """Spider Wiktionary Category:Proto-Algonquian reconstructions."""
    BASE = "https://en.wiktionary.org/w/api.php"
    conn = db(db_path); total = 0; new = 0
    cmcontinue = None

    for _ in range(20):
        params = {"action":"query","list":"categorymembers","format":"json",
                  "cmtitle":"Category:Proto-Algonquian reconstructions",
                  "cmlimit":50,"cmtype":"page"}
        if cmcontinue: params["cmcontinue"] = cmcontinue
        try:
            resp = requests.get(BASE, params=params, timeout=20,
                                headers={"User-Agent":"AlgicResearchBot/1.0"})
            data = resp.json()
        except Exception as e:
            print(f"Wiktionary error: {e}"); break

        for page in data.get("query",{}).get("categorymembers",[]):
            title = page["title"]  # e.g. "Reconstruction:Proto-Algonquian/nipyi"
            if "/nipyi" in title or "Reconstruction:Proto-Algonquian/" in title:
                form = title.split("/")[-1] if "/" in title else title
                proto = f"*{form}"
                # Fetch page content for gloss
                try:
                    pr = requests.get(BASE, params={"action":"parse","page":title,
                                                     "prop":"wikitext","format":"json"},
                                       timeout=15, headers={"User-Agent":"AlgicResearchBot/1.0"})
                    wikitext = pr.json().get("parse",{}).get("wikitext",{}).get("*","")
                    # Extract first gloss: look for ===Noun=== or ===Verb=== followed by # line
                    gloss_m = re.search(r'#\s*([^\n\[{]+)', wikitext)
                    gloss = gloss_m.group(1).strip() if gloss_m else ""
                    # Extract daughter forms
                    daughters = re.findall(r'\*\s*\{\{l\|([a-z]+)\|([^}]+)\}\}', wikitext)
                except Exception:
                    gloss = ""; daughters = []

                total += 1
                set_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"wikt:{proto}"))
                conn.execute("INSERT OR IGNORE INTO cognate_sets(id,proto_form,proto_gloss,source_ref) VALUES(?,?,?,?)",
                             (set_id, proto, gloss, f"https://en.wiktionary.org/wiki/{title.replace(' ','_')}"))
                # Insert proto entry
                eid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"alg:{proto}"))
                r = conn.execute("SELECT id FROM entries WHERE id=?", (eid,)).fetchone()
                if not r:
                    conn.execute("INSERT OR IGNORE INTO entries(id,lang,form,gloss_en,proto_form,source_type,confidence) VALUES(?,?,?,?,?,?,?)",
                                 (eid,"alg",proto,gloss,proto,"wiktionary",0.85))
                    conn.execute("INSERT OR IGNORE INTO cognate_members VALUES(?,?)",(set_id,eid))
                    new += 1

                # Insert daughter forms
                for dlang, dform in daughters:
                    deid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{dlang}:{dform}"))
                    conn.execute("INSERT OR IGNORE INTO entries(id,lang,form,gloss_en,proto_form,source_type,confidence) VALUES(?,?,?,?,?,?,?)",
                                 (deid,dlang,dform,gloss,proto,"wiktionary",0.75))
                    conn.execute("INSERT OR IGNORE INTO cognate_members VALUES(?,?)",(set_id,deid))

            if total >= max_pages: break

        cont = data.get("continue",{})
        cmcontinue = cont.get("cmcontinue")
        if not cmcontinue or total >= max_pages: break
        import time; time.sleep(0.5)

    conn.execute("INSERT INTO import_log(username,action,source,records_in,records_new) VALUES(?,?,?,?,?)",
                 (username,"harvest_wiktionary","wiktionary_pa",total,new))
    conn.commit(); conn.close()
    return total, new


# ── Ollama JSONL export ───────────────────────────────────────────────────────
def export_ollama_jsonl(db_path: str, src_lang: str, tgt_lang: str = "en") -> str:
    conn = db(db_path)
    rows = conn.execute(
        "SELECT form,gloss_en,gloss_fr,gloss_es,proto_form FROM entries "
        "WHERE lang=? AND gloss_en IS NOT NULL AND gloss_en != ''",
        (src_lang,)).fetchall()
    conn.close()

    lang_name = ALGIC.get(src_lang, {}).get("name", src_lang)
    buf = StringIO(); count = 0
    for r in rows:
        form, g_en, g_fr, g_es, proto = r[0],r[1],r[2],r[3],r[4]
        if not form or not g_en: continue
        for inst, inp, out in [
            (f"Translate the following {lang_name} word to English.", form, g_en),
            (f"Translate the following English word to {lang_name}.", g_en, form),
            (f"Identify this language and give the English meaning.", form, f"{lang_name}. English: {g_en}"),
        ]:
            buf.write(json.dumps({"instruction":inst,"input":inp,"output":out},ensure_ascii=False)+"\n")
            count += 1
        if proto:
            buf.write(json.dumps({
                "instruction": f"What is the Proto-Algonquian reconstruction for this {lang_name} word?",
                "input": form, "output": f"Proto-Algonquian {proto} ('{g_en}')"
            }, ensure_ascii=False)+"\n")
            count += 1
    return buf.getvalue()


# ── DB query helpers ──────────────────────────────────────────────────────────
def db_search(q, langs, db_path):
    conn = db(db_path)
    ph = ",".join("?"*len(langs))
    rows = conn.execute(
        f"SELECT lang,form,ipa,gloss_en,gloss_fr,gloss_es,proto_form,morph_seg,confidence "
        f"FROM entries WHERE (form LIKE ? OR gloss_en LIKE ? OR gloss_fr LIKE ? OR gloss_es LIKE ?) "
        f"AND lang IN ({ph}) ORDER BY confidence DESC, lang LIMIT 200",
        [f"%{q}%"]*4 + langs).fetchall()
    conn.close(); return [dict(r) for r in rows]

def db_cognates(word, lang, db_path):
    conn = db(db_path)
    entry = conn.execute("SELECT * FROM entries WHERE lang=? AND form=? LIMIT 1",(lang,word)).fetchone()
    if not entry: conn.close(); return {}
    entry = dict(entry)
    sets = conn.execute("SELECT set_id FROM cognate_members WHERE entry_id=?",(entry["id"],)).fetchall()
    cogs = []
    for s in sets:
        cogs += [dict(r) for r in conn.execute(
            "SELECT e.lang,e.form,e.ipa,e.gloss_en,e.proto_form FROM cognate_members cm "
            "JOIN entries e ON cm.entry_id=e.id WHERE cm.set_id=? AND e.id!=?",
            (s["set_id"],entry["id"])).fetchall()]
    if entry.get("proto_form"):
        cogs += [dict(r) for r in conn.execute(
            "SELECT lang,form,ipa,gloss_en,proto_form FROM entries WHERE proto_form=? AND id!=? LIMIT 30",
            (entry["proto_form"],entry["id"])).fetchall()]
    seen,deduped = set(),[]
    for c in cogs:
        k=(c["lang"],c["form"])
        if k not in seen: seen.add(k); deduped.append(c)
    conn.close(); return {"entry":entry,"cognates":deduped}

def db_stats(db_path):
    conn = db(db_path)
    total = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    by_lang = conn.execute("SELECT lang,COUNT(*) n FROM entries GROUP BY lang ORDER BY n DESC").fetchall()
    log = conn.execute("SELECT ts,username,action,records_in,records_new FROM import_log ORDER BY id DESC LIMIT 20").fetchall()
    conn.close()
    return {"total":total,"by_lang":[dict(r) for r in by_lang],
            "recent_imports":[dict(r) for r in log]}

def db_can_export(db_path, role, fmt):
    conn = db(db_path)
    r = conn.execute("SELECT 1 FROM export_permissions WHERE role=? AND format=?",(role,fmt)).fetchone()
    conn.close(); return r is not None

def ety_chain(word):
    try: return [{"word":o.word,"language":str(o.language)} for o in ety_lib.origins(word.strip().lower(),recursive=True)]
    except: return []

def ety_tree_text(word):
    try:
        import io; t=ety_lib.tree(word.strip().lower()); buf=io.StringIO(); t.show(stdout=buf); return buf.getvalue()
    except: return ""

# ── pyglossary export ─────────────────────────────────────────────────────────
def pyglossary_export(db_path, fmt, lang, min_conf=0.3):
    from pyglossary.glossary_v2 import Glossary
    Glossary.init()
    g = Glossary(); g.setInfo("bookname", f"{ALGIC.get(lang,{}).get('name',lang)} Lexicon")
    conn = db(db_path)
    rows = conn.execute("SELECT form,ipa,pos,gloss_en,gloss_fr,gloss_es,proto_form FROM entries WHERE lang=? AND confidence>=?",(lang,min_conf)).fetchall()
    conn.close()
    for r in rows:
        form,ipa,pos,g_en,g_fr,g_es,proto = r
        if not form: continue
        parts = [f"<i>({pos})</i>" if pos else "",f"<b>EN:</b> {g_en}" if g_en else "",
                 f"<b>FR:</b> {g_fr}" if g_fr else "",f"<b>ES:</b> {g_es}" if g_es else "",
                 f"<b>IPA:</b> /{ipa}/" if ipa else "",f"<b>PA:</b> <i>{proto}</i>" if proto else ""]
        g.addEntry(g.newEntry(word=[form],defi="<br/>".join(p for p in parts if p) or "(no def)",defiFormat="h"))
    out_dir=Path(tempfile.mkdtemp())
    EXT={"Stardict":f"{lang}.ifo","AyanDictSQLite":f"{lang}.db","Json":f"{lang}.json","Csv":f"{lang}.csv","Sql":f"{lang}.sql","HtmlDir":lang}
    out=out_dir/EXT.get(fmt,f"{lang}.out"); g.write(str(out),formatName=fmt); return out


# ── HTML (parchment + Native American theme) ──────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Algic — Etymology & Corpus</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet"/>
<style>
:root{
  --bg:#f2ead8;--surface:#e8dcc0;--surface2:#dfd0a8;--ink:#1c1408;
  --rust:#7a2e0e;--gold:#9a6e1a;--sage:#3a5c2a;--sky:#1a3a5c;
  --muted:#6b5c3a;--border:#c4aa7a;--accent:#b85c1a;
  --tip-bg:#1c1408;--tip-txt:#f2ead8;
  --fn:'IM Fell English',Georgia,serif;--mono:'JetBrains Mono',monospace;
}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--ink);font-family:var(--fn);font-size:17px;line-height:1.65;min-height:100vh;}

/* Geometric border pattern - inspired by Great Lakes beadwork */
body::before{
  content:'';position:fixed;top:0;left:0;right:0;height:6px;
  background:repeating-linear-gradient(90deg,
    var(--rust) 0,var(--rust) 8px, var(--gold) 8px, var(--gold) 16px,
    var(--sage) 16px,var(--sage) 24px, var(--gold) 24px, var(--gold) 32px);
  z-index:100;
}
body::after{
  content:'';position:fixed;bottom:0;left:0;right:0;height:6px;
  background:repeating-linear-gradient(90deg,
    var(--sage) 0,var(--sage) 8px, var(--gold) 8px, var(--gold) 16px,
    var(--rust) 16px,var(--rust) 24px, var(--gold) 24px, var(--gold) 32px);
  z-index:100;
}

/* Subtle paper texture */
body > *{position:relative;}
.layout{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='4' height='4'%3E%3Crect width='4' height='4' fill='%23f2ead8'/%3E%3Ccircle cx='1' cy='1' r='.4' fill='%23c4aa7a22'/%3E%3C/svg%3E");}

header{
  background:var(--ink);color:var(--bg);
  padding:1rem 2rem;margin-top:6px;
  display:flex;align-items:baseline;gap:1.2rem;flex-wrap:wrap;
  border-bottom:3px solid var(--gold);
}
header h1{font-size:1.45rem;font-weight:normal;font-style:italic;letter-spacing:.03em;}
header h1 span{color:var(--gold);}
header .sub{font-family:var(--mono);font-size:.6rem;color:#9a8a6a;letter-spacing:.12em;}
header .user-badge{margin-left:auto;font-family:var(--mono);font-size:.65rem;
  color:var(--gold);background:rgba(255,255,255,.08);
  padding:.2rem .6rem;border-radius:3px;border:1px solid #444;}

.layout{display:grid;grid-template-columns:285px 1fr;min-height:calc(100vh - 62px);margin-bottom:6px;}

aside{
  background:var(--surface);border-right:2px solid var(--border);
  padding:1.1rem 1rem;display:flex;flex-direction:column;gap:.85rem;
  overflow-y:auto;max-height:calc(100vh - 62px);
}

.pt{
  font-family:var(--mono);font-size:.58rem;font-weight:600;
  letter-spacing:.16em;text-transform:uppercase;color:var(--muted);
  border-bottom:1px solid var(--border);padding-bottom:.28rem;margin-bottom:.4rem;
  display:flex;align-items:center;gap:.4rem;
}
.pt .dot{width:6px;height:6px;border-radius:50%;background:var(--gold);flex-shrink:0;}

input[type=text],select,textarea{
  background:rgba(255,255,255,.6);border:1px solid var(--border);border-radius:3px;
  padding:.38rem .6rem;font-family:var(--fn);font-size:.95rem;color:var(--ink);
  outline:none;width:100%;transition:border-color .15s,background .15s;
}
input[type=text]:focus,select:focus,textarea:focus{
  border-color:var(--rust);background:rgba(255,255,255,.9);
  box-shadow:0 0 0 2px rgba(122,46,14,.1);
}
textarea{font-family:var(--mono);font-size:.67rem;resize:vertical;}
select{background:rgba(255,255,255,.6);}

button{
  background:var(--rust);color:var(--bg);border:none;border-radius:3px;
  padding:.38rem .85rem;font-family:var(--mono);font-size:.68rem;
  font-weight:600;letter-spacing:.05em;cursor:pointer;transition:background .15s;
  white-space:nowrap;
}
button:hover{background:var(--ink);}
button.sage{background:var(--sage);}
button.sage:hover{background:#243d1a;}
button.ghost{background:transparent;color:var(--rust);border:1px solid var(--rust);}
button.ghost:hover{background:var(--rust);color:var(--bg);}
.row{display:flex;gap:.35rem;align-items:center;}
.lang-grid{display:grid;grid-template-columns:1fr 1fr;gap:.2rem;}
.lang-grid label{font-size:.78rem;display:flex;align-items:center;gap:.28rem;cursor:pointer;}

/* Auth panel */
.auth-panel{background:rgba(0,0,0,.06);border-radius:4px;padding:.6rem .8rem;}
.auth-panel small{font-family:var(--mono);font-size:.6rem;color:var(--muted);display:block;margin-top:.3rem;}

main{padding:1.4rem 2rem;display:flex;flex-direction:column;gap:1.4rem;overflow-y:auto;max-height:calc(100vh - 62px);}

.results-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(255px,1fr));gap:.75rem;}

.entry-card{
  background:rgba(255,255,255,.55);border:1px solid var(--border);
  border-left:3px solid transparent;border-radius:4px;
  padding:.85rem 1rem;cursor:pointer;
  transition:border-color .15s,box-shadow .15s,background .15s;
}
.entry-card:hover{
  background:rgba(255,255,255,.85);
  border-color:var(--rust);border-left-color:var(--rust);
  box-shadow:2px 3px 10px rgba(0,0,0,.12);
}
.lb{font-family:var(--mono);font-size:.58rem;background:var(--surface2);
  border:1px solid var(--border);border-radius:2px;padding:.07rem .3rem;
  color:var(--muted);display:inline-block;margin-bottom:.2rem;}
.hw{font-size:1.2rem;font-weight:normal;font-style:italic;}
.ipa-txt{font-family:var(--mono);font-size:.72rem;color:var(--muted);}
.gloss{color:var(--sage);font-size:.9rem;}
.proto{font-family:var(--mono);font-size:.66rem;color:var(--sky);margin-top:.16rem;}
.morph{font-family:var(--mono);font-size:.63rem;color:var(--muted);margin-top:.1rem;}

/* Phoneme tooltip — furigana style */
.ph{display:inline;position:relative;cursor:help;}
.ph:hover .tip,.ph:focus .tip{opacity:1;pointer-events:auto;transform:translateX(-50%) translateY(0);}
.tip{
  opacity:0;pointer-events:none;
  position:absolute;bottom:calc(100% + 6px);left:50%;
  transform:translateX(-50%) translateY(4px);
  background:var(--tip-bg);color:var(--tip-txt);
  font-family:var(--mono);font-size:.62rem;line-height:1.5;
  padding:.3rem .55rem;border-radius:3px;
  white-space:nowrap;z-index:500;
  border:1px solid var(--gold);
  transition:opacity .12s,transform .12s;
  box-shadow:0 3px 10px rgba(0,0,0,.4);
}
.tip .sro{color:var(--gold);font-weight:600;}
.tip .ipa-t{color:#7eb8a4;}
.tip::after{content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);
  border:5px solid transparent;border-top-color:var(--tip-bg);}

/* Detail */
.detail{background:rgba(255,255,255,.65);border:1px solid var(--border);
  border-radius:4px;padding:1.4rem 1.8rem;display:none;}
.detail.on{display:block;}
.detail h2{font-size:1.75rem;font-weight:normal;font-style:italic;
  border-bottom:2px solid var(--gold);padding-bottom:.3rem;margin-bottom:.9rem;}
.tabs{display:flex;border-bottom:2px solid var(--border);margin-bottom:.9rem;}
.tab{padding:.3rem 1rem;font-family:var(--mono);font-size:.62rem;letter-spacing:.08em;
  cursor:pointer;border:none;background:transparent;color:var(--muted);
  border-bottom:2px solid transparent;margin-bottom:-2px;}
.tab.on{color:var(--rust);border-bottom-color:var(--rust);font-weight:600;}
.tc{display:none;}.tc.on{display:block;}
.ctable{width:100%;border-collapse:collapse;font-size:.9rem;}
.ctable th{background:var(--surface2);text-align:left;padding:.3rem .65rem;
  font-family:var(--mono);font-size:.6rem;letter-spacing:.08em;
  border-bottom:2px solid var(--border);}
.ctable td{padding:.3rem .65rem;border-bottom:1px solid var(--surface2);}
.ctable tr:hover td{background:rgba(255,255,255,.5);}

/* Etymology */
.ety-chain{display:flex;align-items:center;flex-wrap:wrap;gap:.32rem;margin:.65rem 0;}
.enode{background:var(--surface2);border:1px solid var(--border);border-radius:3px;
  padding:.16rem .5rem;font-size:.8rem;}
.enode .ll{font-family:var(--mono);font-size:.57rem;color:var(--muted);display:block;}
.earr{color:var(--rust);font-size:1.05rem;}
.treepre{font-family:var(--mono);font-size:.72rem;background:var(--surface2);
  border:1px solid var(--border);border-radius:3px;padding:.75rem;
  white-space:pre;overflow-x:auto;line-height:1.5;}

/* Admin section */
.admin-section{background:rgba(122,46,14,.06);border:1px solid rgba(122,46,14,.2);
  border-radius:4px;padding:.75rem .9rem;}
.admin-section .pt .dot{background:var(--rust);}

.status{font-family:var(--mono);font-size:.62rem;color:var(--muted);
  padding:.35rem 0;border-top:1px solid var(--border);margin-top:auto;}
.msg{font-family:var(--mono);font-size:.7rem;padding:.3rem .6rem;border-radius:3px;margin:.3rem 0;}
.msg.ok{background:rgba(58,92,42,.1);color:var(--sage);border:1px solid var(--sage);}
.msg.err{background:rgba(122,46,14,.1);color:var(--rust);border:1px solid var(--rust);}
.nor{text-align:center;padding:2.5rem;color:var(--muted);font-style:italic;}

/* Import log table */
.log-table{width:100%;font-family:var(--mono);font-size:.62rem;border-collapse:collapse;}
.log-table td,.log-table th{padding:.2rem .5rem;border-bottom:1px solid var(--border);}
.log-table th{background:var(--surface2);text-align:left;}
</style>
</head><body>
<header>
  <h1>Algic <span>Etymology</span> &amp; Corpus</h1>
  <span class="sub">MIAMI · KICKAPOO · POTAWATOMI · CREE · SAC · PROTO-ALGONQUIAN</span>
  <span class="user-badge" id="ubadge">not authenticated</span>
</header>
<div class="layout">
<aside>

  <!-- Auth -->
  <div class="auth-panel">
    <div class="pt"><span class="dot"></span>API Key</div>
    <div class="row">
      <input type="password" id="api-key" placeholder="paste key…"/>
      <button onclick="setKey()">Set</button>
    </div>
    <small id="auth-msg">Key stored in session only</small>
  </div>

  <!-- Search -->
  <div>
    <div class="pt"><span class="dot"></span>Search Corpus</div>
    <input type="text" id="q" placeholder="nipi / water / *nipyi"/>
    <div class="row" style="margin-top:.35rem">
      <button onclick="doSearch()">Search</button>
    </div>
  </div>

  <!-- Languages -->
  <div>
    <div class="pt"><span class="dot"></span>Languages</div>
    <div class="lang-grid" id="lc">
      {% for code, info in langs.items() %}
      <label><input type="checkbox" value="{{ code }}"
        {% if info.get('priority') %}checked{% endif %}/>
        {{ info.name }}</label>
      {% endfor %}
    </div>
  </div>

  <!-- English etymology -->
  <div>
    <div class="pt"><span class="dot"></span>Gloss → Etymology</div>
    <input type="text" id="eq" placeholder="water / fire / speak"/>
    <div class="row" style="margin-top:.35rem">
      <button onclick="doEty()">Trace</button>
    </div>
  </div>

  <!-- Export (user) -->
  <div>
    <div class="pt"><span class="dot"></span>Export Dataset</div>
    <select id="el">{% for code,info in langs.items() %}<option value="{{ code }}"{% if code=='mia' %} selected{% endif %}>{{ code }} — {{ info.name }}</option>{% endfor %}</select>
    <div class="row" style="margin-top:.35rem">
      <select id="ef">
        <option value="tmx">TMX 1.4</option>
        <option value="json">JSON</option>
        <option value="csv">CSV</option>
        <option value="Stardict">StarDict</option>
        <option value="AyanDictSQLite">SQLite</option>
        <option value="Sql">SQL</option>
        <option value="ollama-jsonl">Ollama JSONL</option>
      </select>
      <select id="et"><option value="en">→ EN</option><option value="fr">→ FR</option><option value="es">→ ES</option></select>
    </div>
    <button style="margin-top:.35rem;width:100%" onclick="doExport()">Download</button>
  </div>

  <!-- XSLT round-trip -->
  <div>
    <div class="pt"><span class="dot"></span>XSLT Round-Trip</div>
    <select id="xd">
      <option value="lift2tmx">LIFT → TMX</option>
      <option value="lift2xliff">LIFT → XLIFF</option>
      <option value="tmx2lift">TMX → LIFT</option>
      <option value="tmx2xliff">TMX → XLIFF</option>
      <option value="xliff2lift">XLIFF → LIFT</option>
      <option value="xliff2tmx">XLIFF → TMX</option>
      <option value="eaf2tmx">EAF → TMX</option>
      <option value="eaf2xliff">EAF → XLIFF</option>
      <option value="eaf2lift">EAF → LIFT</option>
      <option value="eaf2tei">EAF → TEI</option>
      <option value="tmx2eaf">TMX → EAF</option>
      <option value="tt_tmx">LIFT→PO→TMX (tt)</option>
      <option value="tt_xliff">LIFT→PO→XLIFF (tt)</option>
      <option value="tt_tbx">LIFT→PO→TBX (tt)</option>
      <option value="tt_csv">LIFT→PO→CSV (tt)</option>
    </select>
    <div class="row" style="margin-top:.3rem">
      <input type="text" id="xs" value="mia" style="width:65px"/>
      <input type="text" id="xt" value="en"  style="width:55px"/>
      <button onclick="doXSLT()">Convert</button>
    </div>
    <textarea id="xi" rows="4" placeholder="Paste XML here…"></textarea>
    <textarea id="xo" rows="4" placeholder="Output…" readonly></textarea>
    <button class="ghost" style="margin-top:.3rem;width:100%" onclick="dlXSLT()">↓ Download output</button>
  </div>

  <!-- Admin: import -->
  <div class="admin-section" id="admin-panel" style="display:none">
    <div class="pt"><span class="dot" style="background:var(--rust)"></span>Admin — Import</div>

    <div style="margin-bottom:.5rem">
      <label style="font-size:.8rem">Import TMX / update existing</label>
      <div class="row" style="margin-top:.25rem">
        <input type="text" id="imp-lang" value="mia" style="width:60px"/>
        <button class="sage" onclick="importFile('tmx')">Import TMX</button>
        <button class="sage" onclick="importFile('lift')">Import LIFT</button>
      </div>
      <input type="file" id="imp-file" accept=".tmx,.lift,.xml" style="margin-top:.35rem;font-size:.75rem;"/>
    </div>

    <div style="margin-bottom:.5rem">
      <label style="font-size:.8rem">OLAC OAI-PMH harvest</label>
      <div class="row" style="margin-top:.25rem">
        <input type="text" id="olac-langs" placeholder="mia kic pot" style="flex:1"/>
        <button class="sage" onclick="doOLAC()">Harvest</button>
      </div>
    </div>

    <div>
      <label style="font-size:.8rem">Wiktionary Proto-Algonquian</label>
      <div class="row" style="margin-top:.25rem">
        <input type="number" id="wiki-max" value="200" style="width:70px"/>
        <button class="sage" onclick="doWiktionary()">Spider</button>
      </div>
    </div>

    <div id="imp-msg"></div>
  </div>

  <!-- Admin: import log -->
  <div class="admin-section" id="log-panel" style="display:none">
    <div class="pt"><span class="dot" style="background:var(--sky)"></span>Import Log</div>
    <div id="log-body" style="overflow-x:auto;"></div>
  </div>

  <div class="status" id="st">Ready</div>
</aside>

<main>
  <!-- Etymology chain -->
  <div id="ep" style="display:none">
    <div class="pt"><span class="dot"></span>English Etymology Chain</div>
    <div class="ety-chain" id="ec"></div>
    <div class="treepre" id="et2" style="display:none"></div>
  </div>

  <!-- Results -->
  <div id="ra"><div class="nor">Search the corpus, or use the round-trip panel to convert XML</div></div>

  <!-- Detail -->
  <div class="detail" id="det">
    <h2 id="dw"></h2>
    <div class="tabs">
      <button class="tab on" onclick="stab('cog')">Cognates</button>
      <button class="tab" onclick="stab('ex')">Examples</button>
      <button class="tab" onclick="stab('raw')">Raw</button>
    </div>
    <div class="tc on" id="tc-cog"></div>
    <div class="tc" id="tc-ex"></div>
    <div class="tc" id="tc-raw"></div>
  </div>
</main>
</div>

<script>
// ── Phoneme tables ─────────────────────────────────────────────────────────
// Cree syllabics — from syllabics_transliterator.html (full map)
const SYLLABICS = {{ cree_json | safe }};

// Kickapoo Roman — digraphs first (Voorhis 1974 / SIL McPherson)
const KIC = {{ kic_json | safe }};

// Miami-Illinois Myaamia Roman — digraphs first (Leonard / Costa revised)
const MIA = {{ mia_json | safe }};

// Shared Algonquian (Pot, Sac, Men, Sha, Oji)
const ALGO = {{ alg_json | safe }};

const LANG_TABLE = {{ lang_table_json | safe }};
const LNAMES     = {{ langs_json | safe }};

// ── Tokenizer ──────────────────────────────────────────────────────────────
function annotate(text, lang) {
  if (!text) return '';
  const tblKey = LANG_TABLE[lang] || 'mia';
  const tbl = tblKey === 'syllabics' ? SYLLABICS
            : tblKey === 'kic'       ? KIC
            : tblKey === 'mia'       ? MIA : ALGO;
  const keys = Object.keys(tbl);  // insertion order: digraphs before singles
  let out = '', i = 0;
  while (i < text.length) {
    let matched = false;
    for (const k of keys) {
      if (text.slice(i, i + k.length) === k) {
        const d = tbl[k];
        const sro = d.sro  ? `<span class="sro">${eh(d.sro)}</span> ` : '';
        const ip  = d.ipa  ? `<span class="ipa-t">/${eh(d.ipa)}/</span> ` : '';
        const nt  = d.note || d.notes || '';
        out += `<span class="ph" tabindex="0">${eh(k)}<span class="tip">${sro}${ip}${eh(nt)}</span></span>`;
        i += k.length; matched = true; break;
      }
    }
    if (!matched) { out += eh(text[i]); i++; }
  }
  return out;
}
function eh(s) { return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

// ── State ──────────────────────────────────────────────────────────────────
let API_KEY = '';
const $ = id => document.getElementById(id);
const st = msg => $('st').textContent = msg;
function lname(c) { return LNAMES[c]?.name || c; }
function selLangs() { return [...$('lc').querySelectorAll('input:checked')].map(e=>e.value); }

// ── Auth ───────────────────────────────────────────────────────────────────
function setKey() {
  API_KEY = $('api-key').value.trim();
  fetch('/api/whoami', {headers:{'X-API-Key':API_KEY}})
    .then(r=>r.json()).then(d=>{
      if (d.error) { $('ubadge').textContent='not authenticated'; $('ubadge').style.color='#c44'; }
      else {
        $('ubadge').textContent = `${d.username} [${d.role}]`;
        $('ubadge').style.color = d.role==='admin'?'#f0c060':'#90c890';
        if (d.role==='admin') { $('admin-panel').style.display=''; $('log-panel').style.display=''; loadLog(); }
        $('auth-msg').textContent = `Authenticated as ${d.username}`;
      }
    });
}
function apiHeaders() { return API_KEY ? {'X-API-Key':API_KEY,'Content-Type':'application/json'} : {'Content-Type':'application/json'}; }

// ── Search ─────────────────────────────────────────────────────────────────
async function doSearch() {
  const q=$('q').value.trim(); if(!q) return;
  const langs=selLangs(); if(!langs.length){st('Select a language');return;}
  st('Searching…'); $('det').classList.remove('on');
  const r=await fetch(`/api/search?q=${encodeURIComponent(q)}&langs=${langs.join(',')}`);
  const d=await r.json(); renderRes(d);
  st(`${d.length} result${d.length!==1?'s':''} for "${q}"`);
}
$('q').addEventListener('keydown',e=>{if(e.key==='Enter')doSearch();});

function renderRes(rows) {
  if(!rows.length){$('ra').innerHTML='<div class="nor">No matches in corpus</div>';return;}
  $('ra').innerHTML='<div class="results-grid">'+rows.map(r=>`
    <div class="entry-card" onclick="loadDet('${encodeURIComponent(r.form)}','${r.lang}')">
      <span class="lb">${r.lang} · ${lname(r.lang)}</span>
      <div class="hw">${annotate(r.form, r.lang)}</div>
      ${r.ipa?`<div class="ipa-txt">/${r.ipa}/</div>`:''}
      ${r.gloss_en?`<div class="gloss">${eh(r.gloss_en)}</div>`:''}
      ${r.gloss_fr?`<div class="gloss" style="color:#3a5c2a">fr: ${eh(r.gloss_fr)}</div>`:''}
      ${r.gloss_es?`<div class="gloss" style="color:#5c3a1a">es: ${eh(r.gloss_es)}</div>`:''}
      ${r.proto_form?`<div class="proto">PA: ${eh(r.proto_form)}</div>`:''}
      ${r.morph_seg?`<div class="morph">${eh(r.morph_seg)}</div>`:''}
    </div>`).join('')+'</div>';
}

// ── Detail ─────────────────────────────────────────────────────────────────
async function loadDet(word, lang) {
  word = decodeURIComponent(word); st(`Loading ${word}…`);
  const r=await fetch(`/api/cognates?word=${encodeURIComponent(word)}&lang=${lang}`);
  const d=await r.json(); if(!d.entry){st('Not found');return;}
  $('dw').innerHTML=`${annotate(d.entry.form,lang)} <small style="font-size:.85rem;color:var(--muted)">· ${lname(lang)} (${lang})</small>`;
  $('det').classList.add('on');
  const cogs=d.cognates||[];
  $('tc-cog').innerHTML=cogs.length
    ?`<table class="ctable"><tr><th>Lang</th><th>Form</th><th>IPA</th><th>Gloss</th><th>PA reconstruction</th></tr>
      ${cogs.map(c=>`<tr>
        <td><span class="lb">${c.lang}</span></td>
        <td><strong>${annotate(c.form,c.lang)}</strong></td>
        <td style="font-family:var(--mono);font-size:.74rem">${c.ipa||''}</td>
        <td style="font-style:italic">${eh(c.gloss_en||'')}</td>
        <td style="font-family:var(--mono);font-size:.68rem;color:var(--sky)">${eh(c.proto_form||'')}</td>
      </tr>`).join('')}</table>`
    :'<p style="color:var(--muted);font-style:italic;padding:.8rem 0">No cognates found yet. Import PALA or Wiktionary PA data.</p>';
  $('tc-ex').innerHTML='<p style="color:var(--muted);font-size:.85rem;padding:.5rem 0">Examples loaded from entry detail.</p>';
  $('tc-raw').innerHTML=`<pre class="treepre">${JSON.stringify(d.entry,null,2)}</pre>`;
  stab('cog'); st(`${cogs.length} cognate${cogs.length!==1?'s':''} for ${word}`);
}
function stab(name) {
  document.querySelectorAll('.tab').forEach((t,i)=>t.classList.toggle('on',['cog','ex','raw'][i]===name));
  document.querySelectorAll('.tc').forEach(c=>c.classList.remove('on'));
  $(`tc-${name}`).classList.add('on');
}

// ── Etymology ──────────────────────────────────────────────────────────────
async function doEty() {
  const q=$('eq').value.trim(); if(!q) return; st(`Tracing "${q}"…`);
  const r=await fetch(`/api/ety?word=${encodeURIComponent(q)}`);
  const d=await r.json(); $('ep').style.display='block';
  $('ec').innerHTML=(d.chain||[]).length
    ?d.chain.map((n,i)=>(i?'<span class="earr">←</span>':'')+
        `<span class="enode"><span class="ll">${n.language}</span>${n.word}</span>`).join('')
    :'<span style="color:var(--muted);font-style:italic">No English etymology data</span>';
  if(d.tree){$('et2').style.display='block';$('et2').textContent=d.tree;}
  st(`Etymology: ${(d.chain||[]).length} steps`);
}
$('eq').addEventListener('keydown',e=>{if(e.key==='Enter')doEty();});

// ── XSLT ───────────────────────────────────────────────────────────────────
async function doXSLT() {
  const dir=$('xd').value, xml=$('xi').value.trim(), src=$('xs').value||'mia', tgt=$('xt').value||'en';
  if(!xml){st('Paste XML first');return;} st(`Converting ${dir}…`);
  const resp=await fetch('/api/xslt',{method:'POST',headers:apiHeaders(),
    body:JSON.stringify({direction:dir,xml,src_lang:src,tgt_lang:tgt})});
  const d=await resp.json();
  if(d.error){$('xo').value='ERROR: '+d.error;st('XSLT error');}
  else{$('xo').value=d.output;st(`Done — ${d.output.length} chars`);}
}
function dlXSLT(){
  const out=$('xo').value; if(!out)return;
  const ext=$('xd').value.includes('tmx')?'tmx':$('xd').value.includes('xliff')?'xliff':
             $('xd').value.includes('lift')||$('xd').value.includes('2lift')?'lift':
             $('xd').value.includes('tei')?'xml':$('xd').value.includes('csv')?'csv':'xml';
  const a=document.createElement('a');
  a.href='data:application/xml;charset=utf-8,'+encodeURIComponent(out);
  a.download=`output.${ext}`; a.click();
}

// ── Export ─────────────────────────────────────────────────────────────────
function doExport(){
  const lang=$('el').value,fmt=$('ef').value,tgt=$('et').value;
  st(`Exporting ${lang} → ${fmt}…`);
  const url=`/api/export?lang=${lang}&fmt=${fmt}&tgt=${tgt}&api_key=${encodeURIComponent(API_KEY)}`;
  window.location=url;
  setTimeout(()=>st('Export done'),1500);
}

// ── Admin: import ──────────────────────────────────────────────────────────
function showMsg(text, ok=true) {
  const d=$('imp-msg');
  d.innerHTML=`<div class="msg ${ok?'ok':'err'}">${text}</div>`;
}

async function importFile(type) {
  const file=$('imp-file').files[0]; if(!file){showMsg('Select a file',false);return;}
  const lang=$('imp-lang').value||'mia';
  const fd=new FormData(); fd.append('file',file); fd.append('lang',lang);
  st(`Importing ${type}…`);
  const r=await fetch(`/admin/import/${type}`,{method:'POST',
    headers:{'X-API-Key':API_KEY}, body:fd});
  const d=await r.json();
  if(d.error) showMsg(d.error,false);
  else showMsg(`✓ ${d.total_seen} records seen, ${d.new_inserted} new inserted`);
  loadLog(); st('Import complete');
}

async function doOLAC() {
  const langs=$('olac-langs').value.trim().split(/\s+/).filter(Boolean);
  if(!langs.length){showMsg('Enter language codes',false);return;}
  st('Harvesting OLAC…');
  const r=await fetch('/admin/import/olac',{method:'POST',headers:apiHeaders(),
    body:JSON.stringify({languages:langs,max_records:300})});
  const d=await r.json();
  if(d.error) showMsg(d.error,false);
  else showMsg(`✓ OLAC: ${d.total_seen} seen, ${d.new_inserted} new`);
  loadLog(); st('OLAC harvest done');
}

async function doWiktionary() {
  const max=parseInt($('wiki-max').value)||200;
  st('Spidering Wiktionary PA…');
  const r=await fetch('/admin/import/wiktionary',{method:'POST',headers:apiHeaders(),
    body:JSON.stringify({max_pages:max})});
  const d=await r.json();
  if(d.error) showMsg(d.error,false);
  else showMsg(`✓ Wiktionary PA: ${d.total_seen} seen, ${d.new_inserted} new`);
  loadLog(); st('Wiktionary done');
}

async function loadLog() {
  const r=await fetch('/api/stats');
  const d=await r.json();
  $('log-body').innerHTML=`<table class="log-table">
    <tr><th>Time</th><th>User</th><th>Action</th><th>In</th><th>New</th></tr>
    ${(d.recent_imports||[]).map(l=>`<tr>
      <td>${l.ts.slice(0,16)}</td><td>${l.username}</td><td>${l.action}</td>
      <td>${l.records_in}</td><td>${l.records_new}</td></tr>`).join('')}
  </table>
  <div style="font-family:var(--mono);font-size:.6rem;color:var(--muted);margin-top:.4rem">
    Total entries: ${d.total} &nbsp;|&nbsp;
    ${(d.by_lang||[]).map(l=>`${l.lang}:${l.n}`).join(' ')}
  </div>`;
}

// Stats badge
fetch('/api/stats').then(r=>r.json()).then(d=>{
  // no stats badge in header for this version, log panel shows it
});
</script>
</body></html>"""


# ── Phoneme tables injected to template ──────────────────────────────────────
# Full Cree syllabics map (from syllabics_transliterator.html)
CREE_JSON = """{
  "ᐁ":{"sro":"ê","ipa":"eː","notes":"long ê"},
  "ᐃ":{"sro":"i","ipa":"i","notes":"short i"},
  "ᐄ":{"sro":"î","ipa":"iː","notes":"long î"},
  "ᐅ":{"sro":"o","ipa":"o","notes":"short o"},
  "ᐆ":{"sro":"ô","ipa":"oː","notes":"long ô"},
  "ᐊ":{"sro":"a","ipa":"a","notes":"short a"},
  "ᐋ":{"sro":"â","ipa":"aː","notes":"long â"},
  "ᐯ":{"sro":"pê","ipa":"peː"},"ᐱ":{"sro":"pi","ipa":"pi"},"ᐲ":{"sro":"pî","ipa":"piː"},
  "ᐳ":{"sro":"po","ipa":"po"},"ᐴ":{"sro":"pô","ipa":"poː"},"ᐸ":{"sro":"pa","ipa":"pa"},
  "ᐹ":{"sro":"pâ","ipa":"paː"},"ᑊ":{"sro":"p","ipa":"p","notes":"final"},
  "ᑌ":{"sro":"tê","ipa":"teː"},"ᑎ":{"sro":"ti","ipa":"ti"},"ᑏ":{"sro":"tî","ipa":"tiː"},
  "ᑐ":{"sro":"to","ipa":"to"},"ᑑ":{"sro":"tô","ipa":"toː"},"ᑕ":{"sro":"ta","ipa":"ta"},
  "ᑖ":{"sro":"tâ","ipa":"taː"},"ᑦ":{"sro":"t","ipa":"t","notes":"final"},
  "ᑫ":{"sro":"kê","ipa":"keː"},"ᑭ":{"sro":"ki","ipa":"ki"},"ᑮ":{"sro":"kî","ipa":"kiː"},
  "ᑯ":{"sro":"ko","ipa":"ko"},"ᑰ":{"sro":"kô","ipa":"koː"},"ᑲ":{"sro":"ka","ipa":"ka"},
  "ᑳ":{"sro":"kâ","ipa":"kaː"},"ᒃ":{"sro":"k","ipa":"k","notes":"final"},
  "ᒉ":{"sro":"cê","ipa":"tʃeː"},"ᒋ":{"sro":"ci","ipa":"tʃi"},"ᒌ":{"sro":"cî","ipa":"tʃiː"},
  "ᒍ":{"sro":"co","ipa":"tʃo"},"ᒎ":{"sro":"cô","ipa":"tʃoː"},"ᒐ":{"sro":"ca","ipa":"tʃa"},
  "ᒑ":{"sro":"câ","ipa":"tʃaː"},"ᒡ":{"sro":"c","ipa":"tʃ","notes":"final"},
  "ᒣ":{"sro":"mê","ipa":"meː"},"ᒥ":{"sro":"mi","ipa":"mi"},"ᒦ":{"sro":"mî","ipa":"miː"},
  "ᒧ":{"sro":"mo","ipa":"mo"},"ᒨ":{"sro":"mô","ipa":"moː"},"ᒪ":{"sro":"ma","ipa":"ma"},
  "ᒫ":{"sro":"mâ","ipa":"maː"},"ᒻ":{"sro":"m","ipa":"m","notes":"final"},
  "ᓀ":{"sro":"nê","ipa":"neː"},"ᓂ":{"sro":"ni","ipa":"ni"},"ᓃ":{"sro":"nî","ipa":"niː"},
  "ᓄ":{"sro":"no","ipa":"no"},"ᓅ":{"sro":"nô","ipa":"noː"},"ᓇ":{"sro":"na","ipa":"na"},
  "ᓈ":{"sro":"nâ","ipa":"naː"},"ᓐ":{"sro":"n","ipa":"n","notes":"final"},
  "ᓭ":{"sro":"sê","ipa":"seː"},"ᓯ":{"sro":"si","ipa":"si"},"ᓰ":{"sro":"sî","ipa":"siː"},
  "ᓱ":{"sro":"so","ipa":"so"},"ᓲ":{"sro":"sô","ipa":"soː"},"ᓴ":{"sro":"sa","ipa":"sa"},
  "ᓵ":{"sro":"sâ","ipa":"saː"},"ᔅ":{"sro":"s","ipa":"s","notes":"final"},
  "ᔦ":{"sro":"yê","ipa":"jeː"},"ᔨ":{"sro":"yi","ipa":"ji"},"ᔩ":{"sro":"yî","ipa":"jiː"},
  "ᔪ":{"sro":"yo","ipa":"jo"},"ᔫ":{"sro":"yô","ipa":"joː"},"ᔭ":{"sro":"ya","ipa":"ja"},
  "ᔮ":{"sro":"yâ","ipa":"jaː"},"ᔾ":{"sro":"y","ipa":"j","notes":"final"},
  "ᐍ":{"sro":"wê","ipa":"weː"},"ᐏ":{"sro":"wi","ipa":"wi"},"ᐑ":{"sro":"wî","ipa":"wiː"},
  "ᐓ":{"sro":"wo","ipa":"wo"},"ᐕ":{"sro":"wô","ipa":"woː"},"ᐘ":{"sro":"wa","ipa":"wa"},
  "ᐚ":{"sro":"wâ","ipa":"waː"},"ᐤ":{"sro":"w","ipa":"w","notes":"final w"},
  "ᐦ":{"sro":"h","ipa":"h","notes":"h / aspirate"},
  "ᐧ":{"sro":"w","ipa":"ʷ","notes":"w-dot modifier"},
  "ᓕ":{"sro":"le","ipa":"leː","notes":"Moose Cree"},"ᓗ":{"sro":"lo","ipa":"lo","notes":"Moose Cree"},
  "ᓚ":{"sro":"la","ipa":"la","notes":"Moose Cree"},"ᓪ":{"sro":"l","ipa":"l","notes":"Moose Cree final"},
  "ᕃ":{"sro":"re","ipa":"ɾeː","notes":"East Cree"},"ᕆ":{"sro":"ri","ipa":"ɾi","notes":"East Cree"},
  "ᕋ":{"sro":"ra","ipa":"ɾa","notes":"East Cree"},"ᕐ":{"sro":"r","ipa":"ɾ","notes":"East Cree final"},
  "᙮":{"sro":".","ipa":".","notes":"syllabics full stop"}
}"""

KIC_JSON = """{
  "ck":{"ipa":"kː","note":"geminate/fortis k"},
  "pp":{"ipa":"pː","note":"geminate p"},"tt":{"ipa":"tː","note":"geminate t"},
  "ss":{"ipa":"sː","note":"geminate s"},"šš":{"ipa":"ʃː","note":"geminate sh"},
  "cc":{"ipa":"tʃː","note":"geminate ch"},"hw":{"ipa":"ʍ","note":"voiceless labial glide"},
  "nk":{"ipa":"ŋk","note":"velar nasal+k"},
  "â":{"ipa":"aː","note":"long a"},"ê":{"ipa":"eː","note":"long e"},
  "î":{"ipa":"iː","note":"long i"},"ô":{"ipa":"oː","note":"long o"},
  "š":{"ipa":"ʃ","note":"sh (shoe)"},"θ":{"ipa":"θ","note":"th voiceless (thin)"},
  "ʔ":{"ipa":"ʔ","note":"glottal stop"},"c":{"ipa":"tʃ","note":"ch affricate"},
  "a":{"ipa":"a","note":"low vowel"},"e":{"ipa":"e","note":"mid front"},
  "i":{"ipa":"i","note":"high front"},"o":{"ipa":"o","note":"mid back"},
  "k":{"ipa":"k","note":"velar stop"},"p":{"ipa":"p","note":"bilabial stop"},
  "t":{"ipa":"t","note":"alveolar stop"},"s":{"ipa":"s","note":"alveolar fric."},
  "m":{"ipa":"m","note":"bilabial nasal"},"n":{"ipa":"n","note":"alveolar nasal"},
  "w":{"ipa":"w","note":"labial glide"},"y":{"ipa":"j","note":"palatal glide"},
  "h":{"ipa":"h","note":"glottal / length marker"}
}"""

MIA_JSON = """{
  "aa":{"ipa":"aː","note":"long a"},"ii":{"ipa":"iː","note":"long i"},
  "oo":{"ipa":"oː","note":"long o"},"hk":{"ipa":"hk","note":"h+k cluster"},
  "hw":{"ipa":"ʍ","note":"voiceless labial glide"},"nk":{"ipa":"ŋk","note":"velar nasal+k"},
  "nc":{"ipa":"ntʃ","note":"nasal+affricate"},"šk":{"ipa":"ʃk","note":"sh+k cluster"},
  "š":{"ipa":"ʃ","note":"sh (shoe)"},"č":{"ipa":"tʃ","note":"ch affricate"},
  "ð":{"ipa":"ð","note":"voiced th (this)"},"θ":{"ipa":"θ","note":"voiceless th (thin)"},
  "ʔ":{"ipa":"ʔ","note":"glottal stop"},
  "a":{"ipa":"a","note":"low vowel (short)"},"i":{"ipa":"i","note":"high front (short)"},
  "o":{"ipa":"o~ə","note":"mid / schwa (short)"},"e":{"ipa":"e","note":"mid front"},
  "k":{"ipa":"k","note":"velar stop"},"p":{"ipa":"p","note":"bilabial stop"},
  "t":{"ipa":"t","note":"alveolar stop"},"s":{"ipa":"s","note":"alveolar fric."},
  "m":{"ipa":"m","note":"bilabial nasal"},"n":{"ipa":"n","note":"alveolar nasal"},
  "w":{"ipa":"w","note":"labial glide"},"y":{"ipa":"j","note":"palatal glide"},
  "l":{"ipa":"l","note":"lateral (rare)"},"h":{"ipa":"h","note":"glottal fric."}
}"""

ALG_JSON = """{
  "zh":{"ipa":"ʒ","note":"voiced sh (measure)"},"kw":{"ipa":"kʷ","note":"labialized k"},
  "gw":{"ipa":"ɡʷ","note":"labialized g"},"hs":{"ipa":"hs","note":"aspirated s"},
  "â":{"ipa":"aː","note":"long a"},"ê":{"ipa":"eː","note":"long e"},
  "î":{"ipa":"iː","note":"long i"},"ô":{"ipa":"oː","note":"long o"},
  "š":{"ipa":"ʃ","note":"sh"},"c":{"ipa":"tʃ","note":"ch affricate"},
  "ʔ":{"ipa":"ʔ","note":"glottal stop"}
}"""

LANG_TABLE_JSON = json.dumps({
    "cre":"syllabics","csw":"syllabics",
    "mia":"mia","kic":"kic",
    "pot":"algonquian","sac":"algonquian","men":"algonquian",
    "sha":"algonquian","oji":"algonquian","mic":"algonquian","abe":"algonquian","alg":"mia",
})


# ── Flask app ─────────────────────────────────────────────────────────────────
def create_app(db_path: str, xslt_dir: str) -> Flask:
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)

    def _db_path(): return db_path   # closure for require_role

    @app.route("/")
    def index():
        return render_template_string(HTML,
            langs=ALGIC, langs_json=json.dumps(ALGIC),
            cree_json=CREE_JSON, kic_json=KIC_JSON,
            mia_json=MIA_JSON, alg_json=ALG_JSON,
            lang_table_json=LANG_TABLE_JSON)

    @app.route("/api/whoami")
    def whoami():
        user = get_current_user(db_path)
        if not user: return jsonify({"error":"not authenticated"}), 401
        return jsonify({"username":user["username"],"role":user["role"]})

    @app.route("/api/stats")
    def api_stats(): return jsonify(db_stats(db_path))

    @app.route("/api/search")
    def api_search():
        q=request.args.get("q","").strip()
        langs=[l.strip() for l in request.args.get("langs","mia").split(",") if l.strip()]
        return jsonify(db_search(q,langs,db_path) if q else [])

    @app.route("/api/cognates")
    def api_cognates():
        return jsonify(db_cognates(request.args.get("word",""),request.args.get("lang","mia"),db_path))

    @app.route("/api/ety")
    def api_ety():
        w=request.args.get("word","").strip()
        return jsonify({"word":w,"chain":ety_chain(w),"tree":ety_tree_text(w)})

    @app.route("/api/xslt", methods=["POST"])
    def api_xslt():
        b=request.get_json()
        direction=b.get("direction","lift2tmx"); xml_in=b.get("xml","")
        src=b.get("src_lang","mia"); tgt=b.get("tgt_lang","en")
        try:
            if direction.startswith("tt_"):
                out=tt_convert(xml_in.encode(),src,tgt,direction[3:])
                return jsonify({"output":out.decode(errors="replace")})
            out=saxon_transform(xslt_dir,direction,xml_in.encode(),src,tgt)
            return jsonify({"output":out.decode(errors="replace")})
        except Exception as e:
            return jsonify({"error":str(e)}),400

    @app.route("/api/export")
    def api_export():
        user = get_current_user(db_path)
        role = user["role"] if user else "anonymous"
        lang=request.args.get("lang","mia"); fmt=request.args.get("fmt","tmx")
        tgt=request.args.get("tgt","en"); conf=float(request.args.get("min_conf","0.3"))

        if not db_can_export(db_path, role, fmt) and not db_can_export(db_path, "admin", fmt):
            return jsonify({"error":f"Role '{role}' cannot export format '{fmt}'"}),403

        if fmt == "tmx":
            conn = db(db_path)
            rows = conn.execute("""
                SELECT e1.form,e1.ipa,e1.pos,e2.form,e2.proto_form,e1.confidence
                FROM entries e1
                JOIN cognate_members cm1 ON e1.id=cm1.entry_id
                JOIN cognate_members cm2 ON cm1.set_id=cm2.set_id AND cm2.entry_id!=cm1.entry_id
                JOIN entries e2 ON cm2.entry_id=e2.id
                WHERE e1.lang=? AND e2.lang=? AND e1.confidence>=?
                UNION ALL SELECT form,ipa,pos,gloss_en,proto_form,confidence
                FROM entries WHERE lang=? AND gloss_en IS NOT NULL AND confidence>=?
            """,(lang,tgt,conf,lang,conf)).fetchall()
            conn.close()
            def _e(s): return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            tus=[f'<tu tuid="tu{i}">'
                 f'{"".join([f"<prop type=\"x-ipa\">{_e(r[1])}</prop>" if r[1] else "",f"<prop type=\"x-pa\">{_e(r[4])}</prop>" if r[4] else ""])}'
                 f'<tuv xml:lang="{lang}"><seg>{_e(r[0])}</seg></tuv>'
                 f'<tuv xml:lang="{tgt}"><seg>{_e(r[3])}</seg></tuv></tu>'
                 for i,r in enumerate(rows)]
            content=(f'<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE tmx SYSTEM "tmx14.dtd">'
                     f'<tmx version="1.4"><header creationtool="algic-ety-applet" srclang="{lang}"'
                     f' creationdate="{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}"/>'
                     f'<body>{"".join(tus)}</body></tmx>')
            return Response(content.encode(),mimetype="application/xml",
                headers={"Content-Disposition":f'attachment; filename="{lang}-{tgt}.tmx"'})

        if fmt == "ollama-jsonl":
            content = export_ollama_jsonl(db_path, lang, tgt)
            return Response(content.encode(), mimetype="text/plain",
                headers={"Content-Disposition":f'attachment; filename="{lang}-finetune.jsonl"'})

        if fmt in ("json","csv"):
            conn=db(db_path)
            rows=conn.execute("SELECT form,ipa,pos,gloss_en,gloss_fr,gloss_es,proto_form FROM entries WHERE lang=? AND confidence>=?",(lang,conf)).fetchall()
            conn.close()
            if fmt=="json":
                data=[dict(zip(["form","ipa","pos","gloss_en","gloss_fr","gloss_es","proto_form"],r)) for r in rows]
                return Response(json.dumps(data,ensure_ascii=False).encode(),
                    mimetype="application/json",
                    headers={"Content-Disposition":f'attachment; filename="{lang}.json"'})
            else:
                import csv,io as _io
                buf=_io.StringIO(); w=csv.writer(buf)
                w.writerow(["form","ipa","pos","gloss_en","gloss_fr","gloss_es","proto_form"])
                w.writerows(rows)
                return Response(buf.getvalue().encode(),mimetype="text/csv",
                    headers={"Content-Disposition":f'attachment; filename="{lang}.csv"'})

        try:
            out=pyglossary_export(db_path,fmt,lang,conf)
        except Exception as e:
            return jsonify({"error":str(e)}),500
        if out.is_dir():
            buf=tempfile.NamedTemporaryFile(suffix=".zip",delete=False)
            with zipfile.ZipFile(buf.name,"w") as zf:
                for f in out.rglob("*"):
                    if f.is_file(): zf.write(f,f.relative_to(out.parent))
            return send_file(buf.name,as_attachment=True,download_name=f"{lang}-{fmt.lower()}.zip")
        return send_file(str(out),as_attachment=True,download_name=out.name)

    # ── Admin routes ──────────────────────────────────────────────────────
    @app.route("/admin/import/tmx", methods=["POST"])
    @require_role("admin", _db_path)
    def admin_import_tmx():
        file=request.files.get("file"); lang=request.form.get("lang","mia")
        if not file: return jsonify({"error":"No file"}),400
        try:
            total,new=import_tmx(file.read(),lang,db_path,g.user["username"])
            return jsonify({"total_seen":total,"new_inserted":new})
        except Exception as e:
            return jsonify({"error":str(e)}),400

    @app.route("/admin/import/lift", methods=["POST"])
    @require_role("admin", _db_path)
    def admin_import_lift():
        file=request.files.get("file"); lang=request.form.get("lang","mia")
        if not file: return jsonify({"error":"No file"}),400
        try:
            total,new=import_lift(file.read(),lang,db_path,g.user["username"])
            return jsonify({"total_seen":total,"new_inserted":new})
        except Exception as e:
            return jsonify({"error":str(e)}),400

    @app.route("/admin/import/olac", methods=["POST"])
    @require_role("admin", _db_path)
    def admin_import_olac():
        b=request.get_json()
        langs=b.get("languages",list(ALGIC.keys()))
        max_r=b.get("max_records",300)
        repos=b.get("repos",DEFAULT_OLAC_REPOS)
        total,new=harvest_olac(repos,langs,max_r,db_path,g.user["username"])
        return jsonify({"total_seen":total,"new_inserted":new,"schemas":OLAC_SCHEMAS})

    @app.route("/admin/import/wiktionary", methods=["POST"])
    @require_role("admin", _db_path)
    def admin_import_wiktionary():
        b=request.get_json(); max_p=b.get("max_pages",200)
        total,new=harvest_wiktionary_pa(db_path,max_p,g.user["username"])
        return jsonify({"total_seen":total,"new_inserted":new})

    return app


# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    p=argparse.ArgumentParser(description="Algic Etymology Applet v3")
    p.add_argument("--db",    default="myaamia-corpus.db")
    p.add_argument("--xslt",  default="./xslt",
                   help="Path to XSLT sheets directory (from xslt-linguistics-suite-final.zip)")
    p.add_argument("--port",  type=int, default=5000)
    p.add_argument("--host",  default="127.0.0.1")
    p.add_argument("--debug", action="store_true")
    args=p.parse_args()

    admin_key = init_db(args.db)
    print(f"✅  DB: {args.db}")
    print(f"🔑  Admin API key: {admin_key}")
    print(f"📂  XSLT dir: {args.xslt}")

    xslt_path = Path(args.xslt)
    if not xslt_path.exists():
        print(f"⚠️   XSLT dir not found — ET fallback active. To enable Saxon XSLT 2.0:")
        print(f"     unzip xslt-linguistics-suite-final.zip")
        print(f"     cp -r linguistics-suite/xslt {args.xslt}")
    else:
        sheets = list(xslt_path.glob("*.xsl"))
        print(f"📄  {len(sheets)} XSLT sheets loaded: {[s.name for s in sheets]}")

    print(f"🌐  Open: http://{args.host}:{args.port}")
    create_app(args.db, args.xslt).run(host=args.host, port=args.port, debug=args.debug)
