#!/usr/bin/env python3
"""
weblate_adapter.py
==================
Weblate REST API adapter for the XSLT linguistics pipeline.

Bridges Weblate (translation platform) with the full LIFT/EAF/XLIFF/TMX
transform suite using generateDS Python bindings for typed object access.

Capabilities
------------
  push_xliff()     Upload an XLIFF file to a Weblate component translation
  pull_xliff()     Download translated XLIFF from Weblate
  push_tmx()       Upload a TMX as a glossary to Weblate
  pull_units()     Fetch all translation units as typed generateDS objects
  sync_lift()      Round-trip a LIFT file through Weblate (LIFT→XLIFF→push→pull→XLIFF→LIFT)
  sync_eaf()       Round-trip an EAF file through Weblate (EAF→XLIFF→push→pull→XLIFF→EAF)
  list_components() List all components in a project
  create_component() Bootstrap a new Weblate component from an XLIFF file

Authentication
--------------
  Pass api_key and url, or set env vars:
    WEBLATE_URL   (default: http://localhost/api/)
    WEBLATE_KEY

Usage
-----
  from weblate_adapter import WeblateAdapter
  wba = WeblateAdapter(url="https://hosted.weblate.org/api/", api_key="YOUR_KEY")

  # Push a LIFT-derived XLIFF to Weblate component
  wba.sync_lift(
      lift_path="my_dict.lift",
      project="my-project",
      component="my-dict",
      source_lang="tww",
      target_lang="en"
  )

  # Pull translations back to EAF
  wba.sync_eaf(
      eaf_path="session.eaf",
      project="my-project",
      component="session-01",
      source_lang="tww",
      target_lang="en",
      output_eaf="session_translated.eaf"
  )

Weblate API ref: https://docs.weblate.org/en/latest/api.html
"""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import logging
from pathlib import Path
from typing import Optional

import requests

# ── generateDS bindings (from bindings/ sibling dir) ─────────────────────────
_BINDINGS = Path(__file__).parent.parent / "bindings"
if str(_BINDINGS) not in sys.path:
    sys.path.insert(0, str(_BINDINGS))

import lift_ds
import tmx14_ds
import eaf_ds
import xliff_core_1_2_strict_ds as xliff_ds

# ── Saxon XSLT processor (optional — gracefully degraded) ─────────────────────
try:
    from saxonche import PySaxonProcessor
    _SAXON_AVAILABLE = True
except ImportError:
    _SAXON_AVAILABLE = False

_XSLT_DIR = Path(__file__).parent.parent / "xslt"

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
class WeblateAdapter:
    """
    Weblate REST API adapter wrapping wlc + generateDS bindings.

    Parameters
    ----------
    url     : Weblate API base URL  (env: WEBLATE_URL)
    api_key : Weblate API token     (env: WEBLATE_KEY)
    """

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        timeout: int = 60,
        verify_ssl: bool = True,
    ):
        self.url     = (url     or os.getenv("WEBLATE_URL", "http://localhost/api/")).rstrip("/") + "/"
        self.api_key = api_key  or os.getenv("WEBLATE_KEY", "")
        self.timeout = timeout
        self.verify  = verify_ssl
        self._session = requests.Session()
        if self.api_key:
            self._session.headers["Authorization"] = f"Token {self.api_key}"
        self._session.headers["Accept"] = "application/json"

    # ── Low-level helpers ─────────────────────────────────────────────────────

    def _get(self, path: str, params: dict | None = None) -> dict:
        r = self._session.get(
            self.url + path.lstrip("/"),
            params=params, timeout=self.timeout, verify=self.verify
        )
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, data: dict | None = None,
              files: dict | None = None) -> dict:
        r = self._session.post(
            self.url + path.lstrip("/"),
            data=data, files=files,
            timeout=self.timeout, verify=self.verify
        )
        r.raise_for_status()
        return r.json() if r.content else {}

    def _patch(self, path: str, data: dict) -> dict:
        r = self._session.patch(
            self.url + path.lstrip("/"),
            data=data, timeout=self.timeout, verify=self.verify
        )
        r.raise_for_status()
        return r.json()

    # ── Project / component discovery ─────────────────────────────────────────

    def list_projects(self) -> list[dict]:
        """Return all projects on this Weblate instance."""
        return self._get("projects/").get("results", [])

    def list_components(self, project: str) -> list[dict]:
        """Return all components in *project*."""
        return self._get(f"projects/{project}/components/").get("results", [])

    def list_translations(self, project: str, component: str) -> list[dict]:
        """Return all language translations for *project/component*."""
        return self._get(f"components/{project}/{component}/translations/").get("results", [])

    def list_languages(self) -> list[dict]:
        """Return all languages known to this Weblate instance."""
        return self._get("languages/").get("results", [])

    # ── Component bootstrap ───────────────────────────────────────────────────

    def create_component(
        self,
        project: str,
        name: str,
        slug: str,
        xliff_path: str | Path,
        source_lang: str = "und",
        file_format: str = "xliff",
        vcs: str = "local",
        repo: str = "local:",
    ) -> dict:
        """
        Create a new Weblate component seeded with an XLIFF source file.

        Parameters
        ----------
        project     : Weblate project slug
        name        : Human-readable component name
        slug        : URL slug for the component
        xliff_path  : Path to the source XLIFF file to upload
        source_lang : BCP-47 source language code
        """
        xliff_path = Path(xliff_path)
        with open(xliff_path, "rb") as fh:
            resp = self._post(
                f"projects/{project}/components/",
                data={
                    "name": name,
                    "slug": slug,
                    "file_format": file_format,
                    "filemask": "*.xliff",
                    "template": xliff_path.name,
                    "source_language": source_lang,
                    "vcs": vcs,
                    "repo": repo,
                },
                files={"docfile": (xliff_path.name, fh, "application/xliff+xml")},
            )
        log.info("Created component %s/%s", project, slug)
        return resp

    # ── XLIFF push / pull ─────────────────────────────────────────────────────

    def push_xliff(
        self,
        project: str,
        component: str,
        lang: str,
        xliff_path: str | Path,
        method: str = "translate",
        fuzzy: str = "process",
    ) -> dict:
        """
        Upload an XLIFF file to Weblate.

        Parameters
        ----------
        method  : "translate" | "approve" | "suggest" | "fuzzy" | "replace" | "source"
        fuzzy   : "process" | "mark" | "ignore"
        """
        xliff_path = Path(xliff_path)
        with open(xliff_path, "rb") as fh:
            resp = self._post(
                f"translations/{project}/{component}/{lang}/file/",
                data={"method": method, "fuzzy": fuzzy},
                files={"file": (xliff_path.name, fh, "application/xliff+xml")},
            )
        log.info("Pushed XLIFF → %s/%s/%s (%s units)",
                 project, component, lang, resp.get("count", "?"))
        return resp

    def pull_xliff(
        self,
        project: str,
        component: str,
        lang: str,
        output_path: str | Path | None = None,
    ) -> bytes:
        """
        Download translated XLIFF from Weblate.

        Returns raw XLIFF bytes; also writes to *output_path* if given.
        """
        r = self._session.get(
            self.url + f"translations/{project}/{component}/{lang}/file/",
            timeout=self.timeout, verify=self.verify
        )
        r.raise_for_status()
        data = r.content
        if output_path:
            Path(output_path).write_bytes(data)
            log.info("Pulled XLIFF ← %s/%s/%s → %s", project, component, lang, output_path)
        return data

    # ── TMX glossary push ─────────────────────────────────────────────────────

    def push_tmx(
        self,
        project: str,
        tmx_path: str | Path,
        source_lang: str = "und",
    ) -> dict:
        """
        Upload a TMX file as a Weblate project glossary.

        Parses the TMX with the generateDS tmx14_ds binding first to
        validate structure, then POSTs each TU as a glossary term.
        Invalid TUs (missing seg) are skipped with a warning.
        """
        tmx_path = Path(tmx_path)
        root = tmx14_ds.parse(str(tmx_path), silence=True)
        pushed = 0
        skipped = 0

        for tu in root.get_body().get_tu():
            tuvs   = tu.get_tuv()
            src_tv = next((t for t in tuvs
                           if t.get_anyAttributes_().get("lang", "").lower()
                           == source_lang.lower()), None)
            tgt_tvs = [t for t in tuvs if t is not src_tv]
            if not src_tv or not tgt_tvs:
                skipped += 1
                continue

            src_text = src_tv.get_seg() or ""
            for tgt_tv in tgt_tvs:
                tgt_text = tgt_tv.get_seg() or ""
                tgt_lang = tgt_tv.get_anyAttributes_().get("lang", "")
                if src_text and tgt_text:
                    try:
                        self._post(
                            f"glossary/{project}/terms/",
                            data={
                                "source_language": source_lang,
                                "language": tgt_lang,
                                "source": src_text,
                                "target": tgt_text,
                                "context": tu.get_tuid() or "",
                            }
                        )
                        pushed += 1
                    except requests.HTTPError as exc:
                        log.warning("Glossary push skipped (%s): %s", src_text, exc)
                        skipped += 1

        log.info("TMX glossary push: %d terms pushed, %d skipped", pushed, skipped)
        return {"pushed": pushed, "skipped": skipped}

    # ── Translation unit access (typed) ──────────────────────────────────────

    def pull_units(
        self,
        project: str,
        component: str,
        lang: str,
        q: str | None = None,
    ) -> list[dict]:
        """
        Return all translation units for a language as raw dicts.
        Optionally filter with Weblate search query *q*.
        """
        params = {"format": "json"}
        if q:
            params["q"] = q
        path = f"translations/{project}/{component}/{lang}/units/"
        units: list[dict] = []
        while path:
            page = self._get(path, params=params)
            units.extend(page.get("results", []))
            next_url = page.get("next")
            # strip base URL prefix for next iteration
            path = next_url.replace(self.url, "") if next_url else None
            params = {}  # don't re-send params on paginated requests
        return units

    def pull_units_as_xliff_ds(
        self,
        project: str,
        component: str,
        lang: str,
    ):
        """
        Pull the translated XLIFF and parse it into a generateDS
        xliff_ds.xliff object for typed attribute access.
        """
        raw = self.pull_xliff(project, component, lang)
        with tempfile.NamedTemporaryFile(suffix=".xliff", delete=False) as tf:
            tf.write(raw)
            tf_path = tf.name
        root = xliff_ds.parse(tf_path, silence=True)
        os.unlink(tf_path)
        return root

    # ── High-level round-trip helpers ─────────────────────────────────────────

    def _xslt(self, stylesheet: str, src_file: str, params: dict | None = None) -> str:
        """Run an XSLT 2.0 transform via Saxon HE. Returns result string."""
        if not _SAXON_AVAILABLE:
            raise RuntimeError(
                "saxonche not installed. "
                "Run: pip install saxonche --break-system-packages"
            )
        proc = PySaxonProcessor(license=False)
        xp   = proc.new_xslt30_processor()
        if params:
            for k, v in params.items():
                xp.set_parameter(k, proc.make_string_value(v))
        xsl_path = str(_XSLT_DIR / stylesheet)
        exe      = xp.compile_stylesheet(stylesheet_file=xsl_path)
        result   = exe.transform_to_string(source_file=src_file)
        if proc.exception_occurred:
            msg = proc.error_message
            proc.clear_exception_list()
            raise RuntimeError(f"XSLT error in {stylesheet}: {msg}")
        return result

    def sync_lift(
        self,
        lift_path: str | Path,
        project: str,
        component: str,
        source_lang: str = "und",
        target_lang: str = "en",
        method: str = "translate",
        output_lift: str | Path | None = None,
    ) -> Path:
        """
        Full round-trip: LIFT → XLIFF → Weblate push → pull → XLIFF → LIFT.

        Returns path to the output LIFT file with translations filled in.
        """
        lift_path = Path(lift_path)
        out_lift  = Path(output_lift) if output_lift else lift_path.with_suffix(".wbl.lift")

        with tempfile.TemporaryDirectory() as tmp:
            # 1. LIFT → XLIFF
            xliff_str = self._xslt(
                "lift-to-xliff.xsl", str(lift_path),
                {"source-lang": source_lang, "target-lang": target_lang}
            )
            xliff_in = Path(tmp) / "source.xliff"
            xliff_in.write_text(xliff_str, encoding="utf-8")
            log.info("LIFT→XLIFF: %d chars", len(xliff_str))

            # 2. Push to Weblate
            self.push_xliff(project, component, target_lang, xliff_in, method=method)

            # 3. Pull translated XLIFF
            xliff_out = Path(tmp) / "translated.xliff"
            self.pull_xliff(project, component, target_lang, xliff_out)
            log.info("Pulled XLIFF: %d bytes", xliff_out.stat().st_size)

            # 4. XLIFF → LIFT
            lift_str = self._xslt(
                "xliff-to-lift.xsl", str(xliff_out),
                {"source-lang": source_lang}
            )
            out_lift.write_text(lift_str, encoding="utf-8")

        log.info("sync_lift complete → %s", out_lift)
        return out_lift

    def sync_eaf(
        self,
        eaf_path: str | Path,
        project: str,
        component: str,
        source_lang: str = "und",
        target_lang: str = "en",
        method: str = "translate",
        output_eaf: str | Path | None = None,
    ) -> Path:
        """
        Full round-trip: EAF → XLIFF → Weblate push → pull → TMX → EAF.

        Returns path to the output EAF with translation tiers filled in.
        """
        eaf_path = Path(eaf_path)
        out_eaf  = Path(output_eaf) if output_eaf else eaf_path.with_suffix(".wbl.eaf")

        with tempfile.TemporaryDirectory() as tmp:
            # 1. EAF → XLIFF
            xliff_str = self._xslt(
                "eaf-to-xliff.xsl", str(eaf_path),
                {"source-lang": source_lang, "target-lang": target_lang}
            )
            xliff_in = Path(tmp) / "source.xliff"
            xliff_in.write_text(xliff_str, encoding="utf-8")

            # 2. Push to Weblate
            self.push_xliff(project, component, target_lang, xliff_in, method=method)

            # 3. Pull translated XLIFF → TMX
            xliff_out = Path(tmp) / "translated.xliff"
            raw = self.pull_xliff(project, component, target_lang)
            xliff_out.write_bytes(raw)

            # 4. XLIFF → TMX
            tmx_str = self._xslt("xliff-to-tmx.xsl", str(xliff_out))
            tmx_path = Path(tmp) / "translated.tmx"
            tmx_path.write_text(tmx_str, encoding="utf-8")

            # 5. TMX → EAF (reconstructs annotation tiers)
            eaf_str = self._xslt(
                "tmx-to-eaf.xsl", str(tmx_path),
                {"source-lang": source_lang}
            )
            out_eaf.write_text(eaf_str, encoding="utf-8")

        log.info("sync_eaf complete → %s", out_eaf)
        return out_eaf

    # ── Statistics helpers ────────────────────────────────────────────────────

    def translation_stats(self, project: str, component: str, lang: str) -> dict:
        """Return Weblate translation statistics for a language."""
        return self._get(f"translations/{project}/{component}/{lang}/statistics/")

    def component_stats(self, project: str, component: str) -> list[dict]:
        """Return per-language statistics for all translations of a component."""
        return self._get(
            f"components/{project}/{component}/statistics/"
        ).get("results", [])

    # ── Bulk export helpers ────────────────────────────────────────────────────

    def export_all_xliff(
        self,
        project: str,
        component: str,
        output_dir: str | Path,
    ) -> list[Path]:
        """
        Download XLIFF for every translation language and save to *output_dir*.
        Returns list of written paths.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        written = []
        for trans in self.list_translations(project, component):
            lang     = trans["language"]["code"]
            out_path = output_dir / f"{component}.{lang}.xliff"
            self.pull_xliff(project, component, lang, out_path)
            written.append(out_path)
        return written

    def export_all_as_tmx(
        self,
        project: str,
        component: str,
        output_path: str | Path,
        source_lang: str = "und",
    ) -> Path:
        """
        Export every language translation as a single merged TMX file.
        Uses XLIFF → TMX transform on each language's XLIFF, then merges TUs.
        """
        output_path = Path(output_path)
        if not _SAXON_AVAILABLE:
            raise RuntimeError("saxonche required for TMX export")

        proc  = PySaxonProcessor(license=False)
        all_tus: list[str] = []

        for trans in self.list_translations(project, component):
            lang = trans["language"]["code"]
            if lang == source_lang:
                continue
            raw = self.pull_xliff(project, component, lang)
            with tempfile.NamedTemporaryFile(suffix=".xliff", delete=False) as tf:
                tf.write(raw)
                tf_path = tf.name
            try:
                xp  = proc.new_xslt30_processor()
                exe = xp.compile_stylesheet(
                    stylesheet_file=str(_XSLT_DIR / "xliff-to-tmx.xsl")
                )
                tmx_str = exe.transform_to_string(source_file=tf_path)
                # Extract just the <tu> elements (crude but avoids a full XML parse)
                import re
                tus = re.findall(r'<tu\b.*?</tu>', tmx_str, re.DOTALL)
                all_tus.extend(tus)
            finally:
                os.unlink(tf_path)

        # Wrap in TMX envelope
        tmx_doc = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<tmx version="1.4">\n'
            f'  <header creationtool="weblate_adapter" creationtoolversion="1.0"\n'
            f'          datatype="PlainText" segtype="sentence"\n'
            f'          adminlang="en" srclang="{source_lang}"/>\n'
            '  <body>\n'
            + "\n".join(f"    {tu}" for tu in all_tus)
            + '\n  </body>\n</tmx>\n'
        )
        output_path.write_text(tmx_doc, encoding="utf-8")
        log.info("Exported %d TUs to %s", len(all_tus), output_path)
        return output_path


# ─────────────────────────────────────────────────────────────────────────────
# CLI shim
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    ap = argparse.ArgumentParser(
        description="Weblate adapter for the XSLT linguistics pipeline"
    )
    ap.add_argument("--url",     default=os.getenv("WEBLATE_URL","http://localhost/api/"))
    ap.add_argument("--key",     default=os.getenv("WEBLATE_KEY",""))
    sub = ap.add_subparsers(dest="cmd", required=True)

    # list-projects
    sub.add_parser("list-projects")

    # list-components
    lc = sub.add_parser("list-components")
    lc.add_argument("project")

    # push-xliff
    px = sub.add_parser("push-xliff")
    px.add_argument("project"); px.add_argument("component")
    px.add_argument("lang");    px.add_argument("xliff_path")
    px.add_argument("--method", default="translate")

    # pull-xliff
    pl = sub.add_parser("pull-xliff")
    pl.add_argument("project"); pl.add_argument("component")
    pl.add_argument("lang");    pl.add_argument("output")

    # sync-lift
    sl = sub.add_parser("sync-lift")
    sl.add_argument("lift_path")
    sl.add_argument("project"); sl.add_argument("component")
    sl.add_argument("--source-lang", default="und")
    sl.add_argument("--target-lang", default="en")
    sl.add_argument("--output")

    # sync-eaf
    se = sub.add_parser("sync-eaf")
    se.add_argument("eaf_path")
    se.add_argument("project"); se.add_argument("component")
    se.add_argument("--source-lang", default="und")
    se.add_argument("--target-lang", default="en")
    se.add_argument("--output")

    # export-tmx
    et = sub.add_parser("export-tmx")
    et.add_argument("project"); et.add_argument("component")
    et.add_argument("output"); et.add_argument("--source-lang", default="und")

    # stats
    st = sub.add_parser("stats")
    st.add_argument("project"); st.add_argument("component")

    args = ap.parse_args()
    wba  = WeblateAdapter(url=args.url, api_key=args.key)

    match args.cmd:
        case "list-projects":
            print(json.dumps(wba.list_projects(), indent=2))
        case "list-components":
            print(json.dumps(wba.list_components(args.project), indent=2))
        case "push-xliff":
            r = wba.push_xliff(args.project, args.component,
                               args.lang, args.xliff_path, method=args.method)
            print(json.dumps(r, indent=2))
        case "pull-xliff":
            wba.pull_xliff(args.project, args.component, args.lang, args.output)
        case "sync-lift":
            out = wba.sync_lift(args.lift_path, args.project, args.component,
                                args.source_lang, args.target_lang, output_lift=args.output)
            print(f"Written: {out}")
        case "sync-eaf":
            out = wba.sync_eaf(args.eaf_path, args.project, args.component,
                               args.source_lang, args.target_lang, output_eaf=args.output)
            print(f"Written: {out}")
        case "export-tmx":
            out = wba.export_all_as_tmx(args.project, args.component,
                                        args.output, args.source_lang)
            print(f"Written: {out}")
        case "stats":
            print(json.dumps(wba.component_stats(args.project, args.component), indent=2))
