#!/usr/bin/env python3
"""
pipeline.py
===========
Master CLI for the XSLT linguistics pipeline.

Chains all components:
  XSLT 2.0 transforms  (saxonche)
  generateDS bindings  (typed object access)
  Weblate adapter      (translation platform)
  LibreTranslate       (machine translation)
  Claude prompts       (AI enrichment)

Usage examples
--------------
  # EAF → XLIFF
  python pipeline.py xslt eaf-to-xliff session.eaf --source tww --target en

  # EAF → TMX → all formats
  python pipeline.py convert session.eaf --to tmx xliff lift tei --source tww --target en

  # Push to Weblate, pull back translations, reconstruct EAF
  python pipeline.py weblate sync-eaf session.eaf myproject session01 \\
         --source tww --target en --wl-url https://hosted.weblate.org/api/ --wl-key KEY

  # Machine-translate a LIFT file via LibreTranslate
  python pipeline.py lt translate-lift mydict.lift en fr --lt-url http://localhost:5000

  # Enrich a LIFT file with Claude AI (IPA, domains, etymology)
  python pipeline.py claude enrich-lift mydict.lift "Tuwari" tww

  # Full pipeline: EAF → LIFT → Weblate → Claude enrich → output
  python pipeline.py full session.eaf --source tww --target en \\
         --wl-url http://localhost/api/ --wl-key KEY \\
         --lt-url http://localhost:5000 \\
         --claude-key sk-ant-...

  # List available XSLT transforms
  python pipeline.py xslt --list

  # Validate a file against its XSD schema
  python pipeline.py validate session.eaf eaf
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import tempfile
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
HERE      = Path(__file__).parent.resolve()
XSLT_DIR  = HERE.parent / "xslt"
SCHEMA_DIR= HERE.parent / "schemas"
BINDINGS  = HERE.parent / "bindings"
TOOLS_DIR = HERE

for p in [str(BINDINGS), str(TOOLS_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("pipeline")

# ── Saxon XSLT ────────────────────────────────────────────────────────────────
try:
    from saxonche import PySaxonProcessor
    _SAXON = True
except ImportError:
    _SAXON = False
    log.warning("saxonche not installed — XSLT transforms unavailable")

# ── generateDS bindings ────────────────────────────────────────────────────────
try:
    import lift_ds, tmx14_ds, eaf_ds
    import xliff_core_1_2_strict_ds as xliff_ds
    _BINDINGS_OK = True
except ImportError as e:
    _BINDINGS_OK = False
    log.warning("generateDS bindings not found: %s", e)

# ── Adapters (optional) ────────────────────────────────────────────────────────
try:
    from weblate_adapter import WeblateAdapter
    _WBL = True
except ImportError:
    _WBL = False

try:
    from libretranslate_adapter import LibreTranslateAdapter
    _LT = True
except ImportError:
    _LT = False

try:
    from claude_linguistics_prompts import ClaudeAdapter, PromptLibrary
    _CLAUDE = True
except ImportError:
    _CLAUDE = False

# ── XSLT transform map ────────────────────────────────────────────────────────
TRANSFORMS = {
    # (source_format, target_format) -> stylesheet name
    ("lift",  "xliff"): "lift-to-xliff.xsl",
    ("xliff", "lift"):  "xliff-to-lift.xsl",
    ("lift",  "tmx"):   "lift-to-tmx.xsl",
    ("tmx",   "lift"):  "tmx-to-lift.xsl",
    ("xliff", "tmx"):   "xliff-to-tmx.xsl",
    ("tmx",   "xliff"): "tmx-to-xliff.xsl",
    ("eaf",   "xliff"): "eaf-to-xliff.xsl",
    ("eaf",   "tmx"):   "eaf-to-tmx.xsl",
    ("eaf",   "tei"):   "eaf-to-tei.xsl",
    ("eaf",   "lift"):  "eaf-to-lift.xsl",
    ("tmx",   "eaf"):   "tmx-to-eaf.xsl",
}

FORMAT_EXTENSIONS = {
    "lift":  ".lift",
    "xliff": ".xliff",
    "tmx":   ".tmx",
    "eaf":   ".eaf",
    "tei":   ".tei.xml",
}

SCHEMA_FILES = {
    "eaf":   "eaf.xsd",
    "lift":  "lift.xsd",
    "tmx":   "tmx14.xsd",
    "xliff": "xliff-core-1.2-strict.xsd",
}

def detect_format(path: Path) -> str:
    ext = path.suffix.lower()
    return {".eaf": "eaf", ".lift": "lift", ".tmx": "tmx",
            ".xliff": "xliff", ".xml": "xliff"}.get(ext, "unknown")


def xslt_transform(
    src_file: str,
    stylesheet: str,
    params: dict | None = None,
    output: str | None = None,
) -> str:
    """Run a named XSLT 2.0 transform and return result string."""
    if not _SAXON:
        raise RuntimeError("saxonche not installed")
    proc = PySaxonProcessor(license=False)
    xp   = proc.new_xslt30_processor()
    if params:
        for k, v in params.items():
            xp.set_parameter(k, proc.make_string_value(v))
    xsl_path = str(XSLT_DIR / stylesheet)
    exe      = xp.compile_stylesheet(stylesheet_file=xsl_path)
    result   = exe.transform_to_string(source_file=src_file)
    if proc.exception_occurred:
        msg = proc.error_message; proc.clear_exception_list()
        raise RuntimeError(f"XSLT error: {msg}")
    if output:
        Path(output).write_text(result, encoding="utf-8")
        log.info("Written: %s (%d chars)", output, len(result))
    return result


def xslt_chain(
    src_file: str,
    steps: list[tuple[str, dict]],
    output: str,
) -> str:
    """Run a chain of XSLT transforms, piping output through as input."""
    if not _SAXON:
        raise RuntimeError("saxonche not installed")
    proc    = PySaxonProcessor(license=False)
    current = None

    for i, (stylesheet, params) in enumerate(steps):
        xp  = proc.new_xslt30_processor()
        if params:
            for k, v in params.items():
                xp.set_parameter(k, proc.make_string_value(v))
        xsl_path = str(XSLT_DIR / stylesheet)
        exe      = xp.compile_stylesheet(stylesheet_file=xsl_path)
        if i == 0:
            result = exe.transform_to_string(source_file=src_file)
        else:
            node   = proc.parse_xml(xml_text=current)
            result = exe.transform_to_string(xdm_node=node)
        if proc.exception_occurred:
            msg = proc.error_message; proc.clear_exception_list()
            raise RuntimeError(f"XSLT chain error at step {i}: {msg}")
        current = result

    Path(output).write_text(current, encoding="utf-8")
    log.info("Chain complete → %s (%d chars)", output, len(current))
    return current


def validate_xml(path: str, schema_key: str) -> bool:
    """Validate an XML file against its XSD schema using xmlschema."""
    try:
        import xmlschema
    except ImportError:
        log.warning("xmlschema not installed — run: pip install xmlschema")
        return False
    schema_path = str(SCHEMA_DIR / SCHEMA_FILES[schema_key])
    schema      = xmlschema.XMLSchema(schema_path)
    try:
        schema.validate(path)
        log.info("VALID: %s against %s", path, schema_path)
        return True
    except xmlschema.XMLSchemaValidationError as e:
        log.error("INVALID: %s\n%s", path, e.message)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Command implementations
# ─────────────────────────────────────────────────────────────────────────────

def cmd_xslt(args):
    if args.list:
        print("Available transforms:")
        for (src, tgt), xsl in sorted(TRANSFORMS.items()):
            print(f"  {src:8s} → {tgt:8s}  ({xsl})")
        return

    src_path = Path(args.input)
    src_fmt  = args.from_fmt or detect_format(src_path)
    tgt_fmt  = args.to_fmt
    key      = (src_fmt, tgt_fmt)

    if key not in TRANSFORMS:
        log.error("No transform for %s → %s. Use --list to see available transforms.", src_fmt, tgt_fmt)
        sys.exit(1)

    out = args.output or str(src_path.with_suffix(FORMAT_EXTENSIONS[tgt_fmt]))
    params = {}
    if args.source: params["source-lang"] = args.source
    if args.target: params["target-lang"]  = args.target
    if hasattr(args, "admin") and args.admin: params["admin-lang"] = args.admin

    xslt_transform(str(src_path), TRANSFORMS[key], params, out)


def cmd_convert(args):
    """Convert one source file to multiple output formats."""
    src_path = Path(args.input)
    src_fmt  = args.from_fmt or detect_format(src_path)
    params   = {"source-lang": args.source or "und",
                "target-lang": args.target or "en"}

    for tgt_fmt in args.to:
        key = (src_fmt, tgt_fmt)
        if key not in TRANSFORMS:
            log.warning("No transform for %s → %s — skipping", src_fmt, tgt_fmt)
            continue
        out = str(src_path.with_suffix(FORMAT_EXTENSIONS[tgt_fmt]))
        xslt_transform(str(src_path), TRANSFORMS[key], params, out)


def cmd_validate(args):
    fmt = args.format or detect_format(Path(args.input))
    ok  = validate_xml(args.input, fmt)
    sys.exit(0 if ok else 1)


def cmd_weblate(args):
    if not _WBL:
        log.error("weblate_adapter.py not found in tools/"); sys.exit(1)
    wba = WeblateAdapter(url=args.wl_url, api_key=args.wl_key)

    match args.wl_cmd:
        case "list-projects":
            print(json.dumps(wba.list_projects(), indent=2))
        case "list-components":
            print(json.dumps(wba.list_components(args.project), indent=2))
        case "push-xliff":
            r = wba.push_xliff(args.project, args.component, args.lang, args.file)
            print(json.dumps(r, indent=2))
        case "pull-xliff":
            wba.pull_xliff(args.project, args.component, args.lang, args.output)
        case "sync-lift":
            out = wba.sync_lift(args.file, args.project, args.component,
                                args.source, args.target, output_lift=args.output)
            print(f"Written: {out}")
        case "sync-eaf":
            out = wba.sync_eaf(args.file, args.project, args.component,
                               args.source, args.target, output_eaf=args.output)
            print(f"Written: {out}")
        case "stats":
            print(json.dumps(wba.component_stats(args.project, args.component), indent=2))
        case "export-tmx":
            out = wba.export_all_as_tmx(args.project, args.component,
                                        args.output, args.source)
            print(f"Written: {out}")


def cmd_lt(args):
    if not _LT:
        log.error("libretranslate_adapter.py not found in tools/"); sys.exit(1)
    lt = LibreTranslateAdapter(url=args.lt_url, api_key=args.lt_key,
                               throttle_ms=args.throttle)
    match args.lt_cmd:
        case "languages":
            print(json.dumps(lt.available_languages(), indent=2))
        case "detect":
            print(json.dumps(lt.detect(args.text), indent=2))
        case "translate-text":
            print(lt.translate_text(args.text, args.source, args.target))
        case "translate-lift":
            out = lt.translate_lift(args.file, args.source, args.target, args.output)
            print(f"Written: {out}")
        case "translate-tmx":
            out = lt.translate_tmx(args.file, args.source, args.target, args.output)
            print(f"Written: {out}")
        case "translate-xliff":
            out = lt.translate_xliff(args.file, args.source, args.target, args.output)
            print(f"Written: {out}")
        case "translate-eaf-tier":
            out = lt.translate_eaf_tier(args.file, args.tier_id,
                                        args.source, args.target,
                                        output_path=args.output)
            print(f"Written: {out}")


def cmd_claude(args):
    if not _CLAUDE:
        log.error("claude_linguistics_prompts.py not found"); sys.exit(1)
    cl = ClaudeAdapter(api_key=args.claude_key)

    match args.cl_cmd:
        case "list-prompts":
            for name in PromptLibrary.list_prompts():
                p = PromptLibrary.get(name)
                print(f"  {name:30s}  {p.task}")
        case "ipa":
            r = cl.run(PromptLibrary.IPA_FROM_ORTH,
                       orth=args.orth, lang_name=args.lang_name,
                       lang_code=args.lang_code, lang_family="",
                       known_phonemes="", neighbours="")
            print(json.dumps(r, ensure_ascii=False, indent=2))
        case "gloss":
            r = cl.run(PromptLibrary.LEIPZIG_GLOSS,
                       morphemes=args.morphemes,
                       free_translation=args.translation,
                       source_lang=args.source, gloss_lang=args.target,
                       paradigm_notes="")
            print(json.dumps(r, ensure_ascii=False, indent=2))
        case "enrich-lift":
            out = cl.enrich_lift_file(args.file, args.lang_name,
                                      args.lang_code, output_path=args.output)
            print(f"Written: {out}")
        case "summarise-eaf":
            r = cl.summarise_eaf_session(args.file, args.lang_name, args.lang_code)
            print(json.dumps(r, ensure_ascii=False, indent=2))


def cmd_full(args):
    """
    Full pipeline: EAF/LIFT → XLIFF → Weblate → LibreTranslate → Claude enrich → output.
    Steps that are not configured are skipped gracefully.
    """
    src_path = Path(args.input)
    src_fmt  = detect_format(src_path)
    tmp_dir  = Path(tempfile.mkdtemp(prefix="pipeline_"))
    log.info("Full pipeline: %s → tmp=%s", src_path, tmp_dir)

    current_file = src_path
    current_fmt  = src_fmt

    # Step 1: Convert source to XLIFF if not already
    if current_fmt != "xliff":
        xliff_out = tmp_dir / "source.xliff"
        xslt_transform(
            str(current_file),
            TRANSFORMS[(current_fmt, "xliff")],
            {"source-lang": args.source, "target-lang": args.target},
            str(xliff_out),
        )
        current_file = xliff_out
        current_fmt  = "xliff"
        log.info("Step 1: %s → XLIFF", src_fmt)

    # Step 2: Weblate push/pull (if configured)
    if _WBL and args.wl_url and args.wl_key and args.wl_project:
        wba         = WeblateAdapter(url=args.wl_url, api_key=args.wl_key)
        xliff_wbl   = tmp_dir / "weblate.xliff"
        try:
            wba.push_xliff(args.wl_project, args.wl_component or "auto",
                           args.target, str(current_file))
            wba.pull_xliff(args.wl_project, args.wl_component or "auto",
                           args.target, str(xliff_wbl))
            current_file = xliff_wbl
            log.info("Step 2: Weblate push/pull complete")
        except Exception as exc:
            log.warning("Weblate step failed (continuing): %s", exc)

    # Step 3: LibreTranslate fill gaps (if configured)
    if _LT and args.lt_url:
        lt      = LibreTranslateAdapter(url=args.lt_url, api_key=args.lt_key or "",
                                        throttle_ms=500)
        lt_out  = tmp_dir / "lt_filled.xliff"
        try:
            lt.translate_xliff(str(current_file), args.source, args.target, str(lt_out))
            current_file = lt_out
            log.info("Step 3: LibreTranslate fill complete")
        except Exception as exc:
            log.warning("LibreTranslate step failed (continuing): %s", exc)

    # Step 4: Convert XLIFF → target format
    tgt_fmt = args.output_format or src_fmt
    if tgt_fmt != "xliff" and (current_fmt, tgt_fmt) in TRANSFORMS:
        final_out = Path(args.output or str(src_path.with_suffix(
            FORMAT_EXTENSIONS[tgt_fmt]
        )))
        xslt_transform(
            str(current_file),
            TRANSFORMS[(current_fmt, tgt_fmt)],
            {"source-lang": args.source, "target-lang": args.target},
            str(final_out),
        )
        current_file = final_out
        log.info("Step 4: XLIFF → %s", tgt_fmt)
    else:
        final_out = Path(args.output or str(tmp_dir / f"output{FORMAT_EXTENSIONS.get(tgt_fmt,'.xml')}"))
        import shutil
        shutil.copy(str(current_file), str(final_out))

    # Step 5: Claude enrich LIFT (if target is lift and configured)
    if _CLAUDE and args.claude_key and tgt_fmt == "lift" and args.lang_name:
        cl  = ClaudeAdapter(api_key=args.claude_key)
        out = final_out.with_suffix(".enriched.lift")
        try:
            cl.enrich_lift_file(str(final_out), args.lang_name,
                                args.source, output_path=str(out))
            final_out = out
            log.info("Step 5: Claude enrichment complete")
        except Exception as exc:
            log.warning("Claude step failed (continuing): %s", exc)

    log.info("Pipeline complete → %s", final_out)
    print(f"Output: {final_out}")


# ─────────────────────────────────────────────────────────────────────────────
# Argument parser
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    ap  = argparse.ArgumentParser(prog="pipeline", description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    # ── xslt ──
    xs = sub.add_parser("xslt", help="Run a single XSLT transform")
    xs.add_argument("to_fmt", nargs="?", help="Target format")
    xs.add_argument("input",  nargs="?", help="Input file")
    xs.add_argument("--from",  dest="from_fmt")
    xs.add_argument("--source", default="und")
    xs.add_argument("--target", default="en")
    xs.add_argument("--admin",  default="en")
    xs.add_argument("--output", "-o")
    xs.add_argument("--list",   action="store_true")

    # ── convert ──
    cv = sub.add_parser("convert", help="Convert to multiple output formats")
    cv.add_argument("input")
    cv.add_argument("--to",     nargs="+", required=True)
    cv.add_argument("--from",   dest="from_fmt")
    cv.add_argument("--source", default="und")
    cv.add_argument("--target", default="en")

    # ── validate ──
    vl = sub.add_parser("validate", help="Validate XML against XSD schema")
    vl.add_argument("input")
    vl.add_argument("format", nargs="?", choices=list(SCHEMA_FILES))

    # ── weblate ──
    wl = sub.add_parser("weblate", help="Weblate platform operations")
    wl.add_argument("wl_cmd", choices=[
        "list-projects","list-components","push-xliff","pull-xliff",
        "sync-lift","sync-eaf","stats","export-tmx"
    ])
    wl.add_argument("project",   nargs="?")
    wl.add_argument("component", nargs="?")
    wl.add_argument("file",      nargs="?")
    wl.add_argument("--lang",    default="en")
    wl.add_argument("--source",  default="und")
    wl.add_argument("--target",  default="en")
    wl.add_argument("--output",  "-o")
    wl.add_argument("--wl-url",  default=os.getenv("WEBLATE_URL",""))
    wl.add_argument("--wl-key",  default=os.getenv("WEBLATE_KEY",""))

    # ── lt ──
    lt = sub.add_parser("lt", help="LibreTranslate machine translation")
    lt.add_argument("lt_cmd", choices=[
        "languages","detect","translate-text","translate-lift",
        "translate-tmx","translate-xliff","translate-eaf-tier"
    ])
    lt.add_argument("file",    nargs="?")
    lt.add_argument("source",  nargs="?", default="und")
    lt.add_argument("target",  nargs="?", default="en")
    lt.add_argument("text",    nargs="?")
    lt.add_argument("--tier-id")
    lt.add_argument("--output", "-o")
    lt.add_argument("--lt-url",  default=os.getenv("LIBRETRANSLATE_URL","https://libretranslate.com"))
    lt.add_argument("--lt-key",  default=os.getenv("LIBRETRANSLATE_KEY",""))
    lt.add_argument("--throttle", type=int, default=500)

    # ── claude ──
    cl = sub.add_parser("claude", help="Claude AI linguistics enrichment")
    cl.add_argument("cl_cmd", choices=[
        "list-prompts","ipa","gloss","enrich-lift","summarise-eaf"
    ])
    cl.add_argument("file",      nargs="?")
    cl.add_argument("lang_name", nargs="?", default="")
    cl.add_argument("lang_code", nargs="?", default="und")
    cl.add_argument("--orth");     cl.add_argument("--morphemes"); cl.add_argument("--translation")
    cl.add_argument("--source",  default="und")
    cl.add_argument("--target",  default="en")
    cl.add_argument("--output",  "-o")
    cl.add_argument("--claude-key", default=os.getenv("ANTHROPIC_API_KEY",""))

    # ── full ──
    fl = sub.add_parser("full", help="Full chained pipeline")
    fl.add_argument("input")
    fl.add_argument("--source",        default="und")
    fl.add_argument("--target",        default="en")
    fl.add_argument("--output",        "-o")
    fl.add_argument("--output-format", default=None)
    fl.add_argument("--lang-name",     default="")
    fl.add_argument("--wl-url",        default=os.getenv("WEBLATE_URL",""))
    fl.add_argument("--wl-key",        default=os.getenv("WEBLATE_KEY",""))
    fl.add_argument("--wl-project",    default="")
    fl.add_argument("--wl-component",  default="")
    fl.add_argument("--lt-url",        default=os.getenv("LIBRETRANSLATE_URL",""))
    fl.add_argument("--lt-key",        default=os.getenv("LIBRETRANSLATE_KEY",""))
    fl.add_argument("--claude-key",    default=os.getenv("ANTHROPIC_API_KEY",""))

    return ap


if __name__ == "__main__":
    args = build_parser().parse_args()
    match args.command:
        case "xslt":      cmd_xslt(args)
        case "convert":   cmd_convert(args)
        case "validate":  cmd_validate(args)
        case "weblate":   cmd_weblate(args)
        case "lt":        cmd_lt(args)
        case "claude":    cmd_claude(args)
        case "full":      cmd_full(args)
