
#!/usr/bin/env python3
"""
add_algic_languages.py — MIT

Hot-fixes a LOCAL Django/Weblate install so Algic/Algonquian research
languages (mia, oji, pot, sac, ...) work in TMX/XLIFF import, TTL export,
and Argos training — none of which Django/Weblate natively ship.

This is a hack, not a patch upstream would accept: it regex-edits your
settings.py in place rather than going through Django's app registry
properly. It exists because of the chicken-and-egg problem: you can't get
upstream language support without TMX/XLIFF pairs to prove the language is
used, and you can't build those pairs without upstream support. So: hack
first, beg later (or don't).

Expect it to break on Django/Weblate version changes. Re-run is idempotent
(it won't double-insert a code), but a from-scratch settings.py diff review
after every run is strongly recommended. Not stable. Not upstream. Use on
a local/LAN research box only.

Input format (scripts/algic_codes.txt):
    # comment / section header lines start with '#'
    <iso_code>:<Language Name>
Blank lines and stray formatting are tolerated and reported, not silently
dropped.

Usage:
    python3 add_algic_languages.py algic_codes.txt --settings /path/to/settings.py
    python3 add_algic_languages.py algic_codes.txt --settings /path/to/settings.py --dry-run
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

CODE_RE = re.compile(r"^([a-zA-Z0-9][a-zA-Z0-9\-]{1,15})\s*:\s*(.+)$")

GETTEXT_IMPORT = "from django.utils.translation import gettext_lazy as _"


def parse_codes(path: Path):
    """Yield (code, name) pairs from an algic_codes.txt-style file.
    Malformed lines are reported to stderr and skipped, not silently eaten.
    """
    codes = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # strip inline trailing comments like "xlb:Loup B  # Mots loups"
        if "#" in line:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
        m = CODE_RE.match(line)
        if not m:
            print(f"[warn] {path.name}:{lineno}: couldn't parse {raw!r} — skipping", file=sys.stderr)
            continue
        code, name = m.group(1).strip(), m.group(2).strip()
        if not code or not name:
            print(f"[warn] {path.name}:{lineno}: empty code/name in {raw!r} — skipping", file=sys.stderr)
            continue
        codes.append((code, name))
    return codes


def backup(path: Path) -> Path:
    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    return bak


def patch_basic_languages(text: str, codes):
    """Add missing codes into a BASIC_LANGUAGES = { ... } set literal.
    If BASIC_LANGUAGES isn't found, appends a new block at end of file.
    """
    pattern = re.compile(r"(BASIC_LANGUAGES\s*=\s*\{)(.*?)(\})", re.DOTALL)
    m = pattern.search(text)
    existing_codes = set()
    added = []

    if m:
        body = m.group(2)
        existing_codes = set(re.findall(r"""["']([\w\-]+)["']""", body))
        insert_lines = []
        for code, name in codes:
            if code in existing_codes:
                continue
            insert_lines.append(f'    "{code}",  # {name}')
            added.append(code)
        if insert_lines:
            new_body = body.rstrip()
            if new_body and not new_body.rstrip().endswith(","):
                new_body += ","
            new_body += "\n" + "\n".join(insert_lines) + "\n"
            text = text[: m.start()] + m.group(1) + new_body + m.group(3) + text[m.end():]
    else:
        block_lines = [f'    "{code}",  # {name}' for code, name in codes]
        added = [c for c, _ in codes]
        block = (
            "\n\n# --- Algic/Algonquian research languages "
            "(added by add_algic_languages.py) ---\n"
            "BASIC_LANGUAGES = {\n" + "\n".join(block_lines) + "\n}\n"
        )
        text = text.rstrip() + block

    return text, added, existing_codes


def patch_django_languages(text: str, codes, already_basic: set):
    """Add missing codes into the Django LANGUAGES = [ (code, _('Name')), ... ] list.
    Ensures the gettext_lazy import is present.
    """
    if GETTEXT_IMPORT not in text:
        text = GETTEXT_IMPORT + "\n" + text

    pattern = re.compile(r"(LANGUAGES\s*=\s*\[)(.*?)(\n\s*\])", re.DOTALL)
    m = pattern.search(text)
    existing_codes = set()
    added = []

    if m:
        body = m.group(2)
        existing_codes = set(re.findall(r"""\(\s*["']([\w\-]+)["']""", body))
        insert_lines = []
        for code, name in codes:
            if code in existing_codes:
                continue
            safe_name = name.replace("'", "\\'")
            insert_lines.append(f"    ('{code}', _('{safe_name}')),")
            added.append(code)
        if insert_lines:
            new_body = body.rstrip()
            if new_body and not new_body.rstrip().endswith(","):
                new_body += ","
            new_body += "\n" + "\n".join(insert_lines)
            text = text[: m.start()] + m.group(1) + new_body + m.group(3) + text[m.end():]
    else:
        block_lines = [f"    ('{code}', _('{name}'))," for code, name in codes]
        added = [c for c, _ in codes]
        block = (
            "\n\n# --- Algic/Algonquian research languages "
            "(added by add_algic_languages.py) ---\n"
            "LANGUAGES = [\n" + "\n".join(block_lines) + "\n]\n"
        )
        text = text.rstrip() + block

    return text, added, existing_codes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("codes_file", type=Path, help="path to algic_codes.txt")
    ap.add_argument("--settings", type=Path, required=True, help="path to Weblate/Django settings.py to patch")
    ap.add_argument("--dry-run", action="store_true", help="show what would change, write nothing")
    ap.add_argument("--no-backup", action="store_true", help="skip writing a .bak copy (not recommended)")
    args = ap.parse_args()

    if not args.codes_file.exists():
        sys.exit(f"codes file not found: {args.codes_file}")
    if not args.settings.exists():
        sys.exit(f"settings file not found: {args.settings}")

    codes = parse_codes(args.codes_file)
    if not codes:
        sys.exit("no usable codes parsed — nothing to do")
    print(f"[info] parsed {len(codes)} language codes from {args.codes_file}")

    original = args.settings.read_text(encoding="utf-8")
    text = original

    text, added_basic, _ = patch_basic_languages(text, codes)
    text, added_django, _ = patch_django_languages(text, codes, set(added_basic))

    if text == original:
        print("[info] no changes needed — settings.py already has all codes")
        return

    print(f"[info] BASIC_LANGUAGES: +{len(added_basic)} ({', '.join(added_basic) or 'none'})")
    print(f"[info] LANGUAGES:       +{len(added_django)} ({', '.join(added_django) or 'none'})")

    if args.dry_run:
        print("[dry-run] no files written")
        return

    if not args.no_backup:
        bak = backup(args.settings)
        print(f"[info] backed up original to {bak}")

    args.settings.write_text(text, encoding="utf-8")
    print(f"[info] patched {args.settings}")
    print("[warn] experimental hack — restart weblate/django and verify before trusting it")


if __name__ == "__main__":
    main()
