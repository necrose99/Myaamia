#!/usr/bin/env python3
"""
libretranslate_adapter.py
=========================
LibreTranslate REST API adapter for the XSLT linguistics pipeline.

Integrates LibreTranslate (https://libretranslate.com / self-hosted) with
the LIFT/EAF/XLIFF/TMX ecosystem. Uses generateDS bindings for typed
object-level access to each format during translation.

Supported operations
--------------------
  translate_text()        Translate a single string
  translate_lift()        Translate all glosses in a LIFT file
  translate_tmx()         Translate TMX seg elements (source → target)
  translate_xliff()       Fill <target> elements in an XLIFF file
  translate_eaf_tier()    Translate a specific EAF tier's annotation values
  detect()                Detect language of a text snippet
  available_languages()   List language pairs available on the endpoint

Authentication
--------------
  Pass api_key, or set env var LIBRETRANSLATE_KEY.
  For self-hosted instances with no key, leave api_key blank.
  Set LIBRETRANSLATE_URL to point at your instance (default: public API).

Usage
-----
  from libretranslate_adapter import LibreTranslateAdapter

  lt = LibreTranslateAdapter(
      url="https://libretranslate.com",
      api_key="YOUR_KEY"
  )

  # Translate all English glosses in a LIFT file to French
  lt.translate_lift(
      "my_dict.lift",
      source_lang="en",
      target_lang="fr",
      output_path="my_dict_fr.lift"
  )

  # Fill missing targets in an XLIFF file
  lt.translate_xliff(
      "session.xliff",
      source_lang="tww",
      target_lang="en",
      output_path="session_en.xliff"
  )

LibreTranslate API ref: https://libretranslate.com/docs
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from copy import deepcopy
from pathlib import Path
from typing import Optional

import requests

_BINDINGS = Path(__file__).parent.parent / "bindings"
if str(_BINDINGS) not in sys.path:
    sys.path.insert(0, str(_BINDINGS))

import lift_ds
import tmx14_ds
import eaf_ds
import xliff_core_1_2_strict_ds as xliff_ds

log = logging.getLogger(__name__)

# LibreTranslate language codes that map to BCP-47 / LIFT codes
_LANG_MAP = {
    "und": "auto",   # auto-detect for unknown vernaculars
}


def _lt_lang(code: str) -> str:
    """Map a BCP-47/LIFT code to a LibreTranslate language code."""
    return _LANG_MAP.get(code, code.split("-")[0].lower())


class LibreTranslateAdapter:
    """
    Adapter connecting LibreTranslate to the linguistics XSLT pipeline.

    Parameters
    ----------
    url     : LibreTranslate base URL     (env: LIBRETRANSLATE_URL)
    api_key : API key if required         (env: LIBRETRANSLATE_KEY)
    throttle_ms : ms delay between calls  (rate-limit compliance)
    """

    DEFAULT_URL = "https://libretranslate.com"

    def __init__(
        self,
        url:          str | None = None,
        api_key:      str | None = None,
        throttle_ms:  int        = 0,
        timeout:      int        = 30,
        verify_ssl:   bool       = True,
    ):
        self.url         = (url or os.getenv("LIBRETRANSLATE_URL", self.DEFAULT_URL)).rstrip("/")
        self.api_key     = api_key or os.getenv("LIBRETRANSLATE_KEY", "")
        self.throttle    = throttle_ms / 1000.0
        self.timeout     = timeout
        self.verify      = verify_ssl
        self._session    = requests.Session()
        self._session.headers["Content-Type"] = "application/json"

    # ── Core API calls ────────────────────────────────────────────────────────

    def _payload(self, extra: dict) -> dict:
        base = {}
        if self.api_key:
            base["api_key"] = self.api_key
        return {**base, **extra}

    def translate_text(
        self,
        text:        str,
        source_lang: str,
        target_lang: str,
    ) -> str:
        """
        Translate a single text string.

        Parameters
        ----------
        source_lang : BCP-47 code or "auto" for detection
        target_lang : BCP-47 target code
        """
        if not text or not text.strip():
            return text

        src = _lt_lang(source_lang)
        tgt = _lt_lang(target_lang)

        r = self._session.post(
            f"{self.url}/translate",
            json=self._payload({
                "q":      text,
                "source": src,
                "target": tgt,
                "format": "text",
            }),
            timeout=self.timeout,
            verify=self.verify,
        )
        r.raise_for_status()

        if self.throttle:
            time.sleep(self.throttle)

        return r.json().get("translatedText", text)

    def detect(self, text: str) -> list[dict]:
        """Return language detection results for *text*."""
        r = self._session.post(
            f"{self.url}/detect",
            json=self._payload({"q": text}),
            timeout=self.timeout, verify=self.verify
        )
        r.raise_for_status()
        return r.json()

    def available_languages(self) -> list[dict]:
        """Return list of available language pairs."""
        params = {}
        if self.api_key:
            params["api_key"] = self.api_key
        r = self._session.get(
            f"{self.url}/languages",
            params=params, timeout=self.timeout, verify=self.verify
        )
        r.raise_for_status()
        return r.json()

    # ── LIFT translation ──────────────────────────────────────────────────────

    def translate_lift(
        self,
        lift_path:   str | Path,
        source_lang: str,
        target_lang: str,
        output_path: str | Path | None = None,
        add_sense:   bool = True,
    ) -> Path:
        """
        Translate LIFT glosses from *source_lang* to *target_lang*.

        For each sense that has a gloss in *source_lang* but no gloss in
        *target_lang*, a new gloss element is added (when *add_sense* is True).

        Modifies the generateDS object tree in place and writes to *output_path*.
        """
        lift_path   = Path(lift_path)
        output_path = Path(output_path) if output_path else lift_path.with_suffix(
            f".lt_{target_lang}.lift"
        )
        root = lift_ds.parse(str(lift_path), silence=True)

        translated = 0
        skipped    = 0

        for entry in root.get_entry():
            for sense in entry.get_sense():
                existing_langs = {g.get_lang() for g in sense.get_gloss()}

                if target_lang in existing_langs:
                    continue  # already has target gloss

                # Find source gloss to translate from
                src_gloss = next(
                    (g for g in sense.get_gloss() if g.get_lang() == source_lang),
                    None
                )
                if not src_gloss:
                    skipped += 1
                    continue

                src_text = src_gloss.get_text() or ""
                if not src_text.strip():
                    skipped += 1
                    continue

                try:
                    tgt_text = self.translate_text(src_text, source_lang, target_lang)
                except Exception as exc:
                    log.warning("Translation failed for %r: %s", src_text, exc)
                    skipped += 1
                    continue

                if add_sense:
                    new_gloss = lift_ds.gloss()
                    new_gloss.set_lang(target_lang)
                    new_gloss.set_text(tgt_text)
                    sense.get_gloss().append(new_gloss)
                    translated += 1
                    log.debug("  %r → %r  [%s→%s]", src_text, tgt_text,
                              source_lang, target_lang)

                # Also translate definitions
                for defn in sense.get_definition():
                    existing_def_langs = {f.get_lang() for f in defn.get_form()}
                    if target_lang not in existing_def_langs:
                        src_form = next(
                            (f for f in defn.get_form() if f.get_lang() == source_lang),
                            None
                        )
                        if src_form and src_form.get_text():
                            try:
                                tgt_def = self.translate_text(
                                    src_form.get_text(), source_lang, target_lang
                                )
                                new_form = lift_ds.form()
                                new_form.set_lang(target_lang)
                                new_form.set_text(tgt_def)
                                defn.get_form().append(new_form)
                            except Exception as exc:
                                log.warning("Definition translation failed: %s", exc)

        with open(output_path, "w", encoding="utf-8") as fh:
            root.export(fh, 0)

        log.info("translate_lift: %d glosses translated, %d skipped → %s",
                 translated, skipped, output_path)
        return output_path

    # ── TMX translation ───────────────────────────────────────────────────────

    def translate_tmx(
        self,
        tmx_path:    str | Path,
        source_lang: str,
        target_lang: str,
        output_path: str | Path | None = None,
    ) -> Path:
        """
        Add a new target-language TUV to each TU in a TMX file.

        Translates the source TUV's seg text and inserts a new TUV.
        Existing target TUVs in *target_lang* are left unchanged.
        """
        tmx_path    = Path(tmx_path)
        output_path = Path(output_path) if output_path else tmx_path.with_suffix(
            f".lt_{target_lang}.tmx"
        )
        root = tmx14_ds.parse(str(tmx_path), silence=True)

        translated = 0
        skipped    = 0

        for tu in root.get_body().get_tu():
            tuvs = tu.get_tuv()
            existing_langs = {
                t.get_anyAttributes_().get("lang", "").lower()
                for t in tuvs
            }

            if target_lang.lower() in existing_langs:
                continue

            src_tuv = next(
                (t for t in tuvs
                 if t.get_anyAttributes_().get("lang", "").lower()
                 == source_lang.lower()),
                None
            )
            if not src_tuv:
                skipped += 1
                continue

            src_text = src_tuv.get_seg() or ""
            if not src_text.strip():
                skipped += 1
                continue

            try:
                tgt_text = self.translate_text(src_text, source_lang, target_lang)
            except Exception as exc:
                log.warning("TMX translation failed for %r: %s", src_text, exc)
                skipped += 1
                continue

            new_tuv = tmx14_ds.tuv()
            new_tuv.set_seg(tgt_text)
            new_tuv.get_anyAttributes_()["lang"] = target_lang
            tuvs.append(new_tuv)
            translated += 1

        with open(output_path, "w", encoding="utf-8") as fh:
            root.export(fh, 0)

        log.info("translate_tmx: %d TUs translated, %d skipped → %s",
                 translated, skipped, output_path)
        return output_path

    # ── XLIFF translation ─────────────────────────────────────────────────────

    def translate_xliff(
        self,
        xliff_path:  str | Path,
        source_lang: str,
        target_lang: str,
        output_path: str | Path | None = None,
        overwrite:   bool = False,
    ) -> Path:
        """
        Fill empty <target> elements in an XLIFF file via LibreTranslate.

        Only fills trans-units where <target> is absent or empty.
        Set *overwrite=True* to re-translate units that already have targets.

        Uses a minimal approach: reads XLIFF as text via generateDS,
        translates source text, writes target text back.
        """
        xliff_path  = Path(xliff_path)
        output_path = Path(output_path) if output_path else xliff_path.with_suffix(
            f".lt_{target_lang}.xliff"
        )
        root = xliff_ds.parse(str(xliff_path), silence=True)

        translated = 0
        skipped    = 0

        for file_elem in root.get_file():
            for tu in file_elem.get_body().get_trans_unit():
                src_text = _extract_xliff_text(tu.get_source())
                tgt_obj  = tu.get_target()
                tgt_text = _extract_xliff_text(tgt_obj) if tgt_obj else ""

                if tgt_text.strip() and not overwrite:
                    continue  # already translated

                if not src_text.strip():
                    skipped += 1
                    continue

                try:
                    new_text = self.translate_text(src_text, source_lang, target_lang)
                except Exception as exc:
                    log.warning("XLIFF translation failed for %r: %s", src_text, exc)
                    skipped += 1
                    continue

                # Set target
                if tgt_obj is None:
                    new_tgt = xliff_ds.target()
                    tu.set_target(new_tgt)
                    tgt_obj = new_tgt
                # generateDS target is a mixed-content type; set valueOf_
                if hasattr(tgt_obj, "set_valueOf_"):
                    tgt_obj.set_valueOf_(new_text)
                elif hasattr(tgt_obj, "original_tagname_"):
                    # Fallback: store in anyAttributes for inspection
                    tgt_obj.get_anyAttributes_()["_translated_text"] = new_text

                # Set xml:lang attribute on target
                if hasattr(tgt_obj, "set_lang"):
                    tgt_obj.set_lang(target_lang)
                elif hasattr(tgt_obj, "get_anyAttributes_"):
                    tgt_obj.get_anyAttributes_()[
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    ] = target_lang

                translated += 1

        with open(output_path, "w", encoding="utf-8") as fh:
            root.export(fh, 0)

        log.info("translate_xliff: %d units translated, %d skipped → %s",
                 translated, skipped, output_path)
        return output_path

    # ── EAF tier translation ──────────────────────────────────────────────────

    def translate_eaf_tier(
        self,
        eaf_path:      str | Path,
        tier_id:       str,
        source_lang:   str,
        target_lang:   str,
        new_tier_id:   str | None = None,
        output_path:   str | Path | None = None,
        ling_type:     str = "trans-type",
    ) -> Path:
        """
        Translate all annotations in a named EAF tier, writing a new tier.

        Parameters
        ----------
        tier_id     : Source tier to translate (e.g. "trans-en@SP1")
        new_tier_id : Output tier ID (default: "trans-{target_lang}@SP1")
        ling_type   : LINGUISTIC_TYPE_REF for the new tier
        """
        eaf_path    = Path(eaf_path)
        output_path = Path(output_path) if output_path else eaf_path.with_suffix(
            f".lt_{target_lang}.eaf"
        )
        new_tier_id = new_tier_id or f"trans-{target_lang}@SP1"

        root  = eaf_ds.parse(str(eaf_path), silence=True)
        tiers = {t.get_TIER_ID(): t for t in root.get_TIER()}

        if tier_id not in tiers:
            raise ValueError(
                f"Tier {tier_id!r} not found. Available: {list(tiers)}"
            )

        src_tier = tiers[tier_id]

        # Check if target tier already exists
        if new_tier_id in tiers:
            log.info("Target tier %r already exists; updating in place", new_tier_id)
            tgt_tier = tiers[new_tier_id]
            tgt_tier.get_ANNOTATION().clear()
        else:
            tgt_tier = eaf_ds.TIER()
            tgt_tier.set_TIER_ID(new_tier_id)
            tgt_tier.set_LINGUISTIC_TYPE_REF(ling_type)
            tgt_tier.set_PARTICIPANT(src_tier.get_PARTICIPANT() or "SP1")
            # New tier references same parent as source tier
            if src_tier.get_PARENT_REF():
                tgt_tier.set_PARENT_REF(src_tier.get_PARENT_REF())
            root.get_TIER().append(tgt_tier)

        ann_counter = _max_annotation_id(root) + 1
        translated  = 0
        skipped     = 0

        for ann in src_tier.get_ANNOTATION():
            ref_ann = ann.get_REF_ANNOTATION()
            if not ref_ann:
                skipped += 1
                continue

            src_text = ref_ann.get_ANNOTATION_VALUE() or ""
            if not src_text.strip():
                skipped += 1
                continue

            try:
                tgt_text = self.translate_text(src_text, source_lang, target_lang)
            except Exception as exc:
                log.warning("EAF tier translation failed for %r: %s", src_text, exc)
                skipped += 1
                continue

            new_ref = eaf_ds.REF_ANNOTATION()
            new_ref.set_ANNOTATION_ID(f"a{ann_counter}")
            new_ref.set_ANNOTATION_REF(ref_ann.get_ANNOTATION_REF())
            new_ref.set_ANNOTATION_VALUE(tgt_text)
            ann_counter += 1

            new_ann = eaf_ds.ANNOTATION()
            new_ann.set_REF_ANNOTATION(new_ref)
            tgt_tier.get_ANNOTATION().append(new_ann)
            translated += 1

        with open(output_path, "w", encoding="utf-8") as fh:
            root.export(fh, 0)

        log.info("translate_eaf_tier: %d annotations translated, %d skipped → %s",
                 translated, skipped, output_path)
        return output_path

    # ── Batch helpers ─────────────────────────────────────────────────────────

    def translate_tmx_all_targets(
        self,
        tmx_path:     str | Path,
        source_lang:  str,
        target_langs: list[str],
        output_dir:   str | Path | None = None,
    ) -> dict[str, Path]:
        """
        Translate a TMX file into multiple target languages.
        Returns {lang: output_path} mapping.
        """
        tmx_path   = Path(tmx_path)
        output_dir = Path(output_dir) if output_dir else tmx_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {}
        for lang in target_langs:
            out = output_dir / f"{tmx_path.stem}.{lang}.tmx"
            self.translate_tmx(tmx_path, source_lang, lang, out)
            results[lang] = out
        return results


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _extract_xliff_text(elem) -> str:
    """Extract plain text content from an XLIFF source/target element."""
    if elem is None:
        return ""
    if hasattr(elem, "get_valueOf_"):
        return elem.get_valueOf_() or ""
    if hasattr(elem, "get_mixedclass_"):
        # Mixed content — join text parts
        parts = []
        for item in (elem.get_mixedclass_() or []):
            if hasattr(item, "value") and isinstance(item.value, str):
                parts.append(item.value)
        return "".join(parts)
    return str(elem) if elem else ""


def _max_annotation_id(root) -> int:
    """Return highest numeric annotation ID in the EAF document."""
    max_id = 0
    for tier in root.get_TIER():
        for ann in tier.get_ANNOTATION():
            for node in [ann.get_ALIGNABLE_ANNOTATION(), ann.get_REF_ANNOTATION()]:
                if node and hasattr(node, "get_ANNOTATION_ID"):
                    try:
                        n = int("".join(c for c in (node.get_ANNOTATION_ID() or "")
                                        if c.isdigit()))
                        max_id = max(max_id, n)
                    except ValueError:
                        pass
    return max_id


# ─────────────────────────────────────────────────────────────────────────────
# CLI shim
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    ap = argparse.ArgumentParser(
        description="LibreTranslate adapter for the XSLT linguistics pipeline"
    )
    ap.add_argument("--url",
                    default=os.getenv("LIBRETRANSLATE_URL",
                                      LibreTranslateAdapter.DEFAULT_URL))
    ap.add_argument("--key",     default=os.getenv("LIBRETRANSLATE_KEY", ""))
    ap.add_argument("--throttle-ms", type=int, default=500)
    sub = ap.add_subparsers(dest="cmd", required=True)

    # languages
    sub.add_parser("languages")

    # detect
    det = sub.add_parser("detect")
    det.add_argument("text")

    # translate-text
    tt = sub.add_parser("translate-text")
    tt.add_argument("text"); tt.add_argument("source"); tt.add_argument("target")

    # translate-lift
    tl = sub.add_parser("translate-lift")
    tl.add_argument("lift_path")
    tl.add_argument("source"); tl.add_argument("target")
    tl.add_argument("--output")

    # translate-tmx
    tm = sub.add_parser("translate-tmx")
    tm.add_argument("tmx_path")
    tm.add_argument("source"); tm.add_argument("target")
    tm.add_argument("--output")

    # translate-xliff
    tx = sub.add_parser("translate-xliff")
    tx.add_argument("xliff_path")
    tx.add_argument("source"); tx.add_argument("target")
    tx.add_argument("--output")
    tx.add_argument("--overwrite", action="store_true")

    # translate-eaf-tier
    te = sub.add_parser("translate-eaf-tier")
    te.add_argument("eaf_path"); te.add_argument("tier_id")
    te.add_argument("source"); te.add_argument("target")
    te.add_argument("--new-tier-id")
    te.add_argument("--output")

    args = ap.parse_args()
    lt   = LibreTranslateAdapter(
        url=args.url, api_key=args.key,
        throttle_ms=args.throttle_ms
    )

    match args.cmd:
        case "languages":
            print(json.dumps(lt.available_languages(), indent=2))
        case "detect":
            print(json.dumps(lt.detect(args.text), indent=2))
        case "translate-text":
            print(lt.translate_text(args.text, args.source, args.target))
        case "translate-lift":
            out = lt.translate_lift(args.lift_path, args.source, args.target, args.output)
            print(f"Written: {out}")
        case "translate-tmx":
            out = lt.translate_tmx(args.tmx_path, args.source, args.target, args.output)
            print(f"Written: {out}")
        case "translate-xliff":
            out = lt.translate_xliff(args.xliff_path, args.source, args.target,
                                     args.output, overwrite=args.overwrite)
            print(f"Written: {out}")
        case "translate-eaf-tier":
            out = lt.translate_eaf_tier(
                args.eaf_path, args.tier_id, args.source, args.target,
                new_tier_id=args.new_tier_id, output_path=args.output
            )
            print(f"Written: {out}")
