#!/usr/bin/env python3
"""
tmx_to_xliff2.py

TMX -> XLIFF 2.2 converter that preserves custom <prop> metadata
(IPA transcriptions, ILDA/upstream URLs, ISBN, scientific names,
form-type, letter grouping, part-of-speech, etc.) instead of
discarding it the way a plain TMX 1.4 -> XLIFF 1.2 pass does.

Based partially on:
https://github.com/andresromeroarcas/tmx-to-xliff/blob/main/tmx-to-xliff_basic.py

Why XLIFF 2.2 instead of 1.2:
XLIFF 1.2 has no first-class place for arbitrary <prop type="..."> data
on a trans-unit; people either lose it or stuff it into <note>, which
isn't machine-queryable. XLIFF 2.x's Metadata module (<mda:metadata>)
gives each <unit> and each per-language <segment>/<source>/<target>
a structured, extensible bag of key/value groups that round-trips
cleanly and is still valid, spec-conformant XLIFF.

Known custom prop types this script understands and maps by name
(anything else still gets carried through, just ungrouped):
    x-ipa-mia         -> IPA transcription (language-specific romanization)
    ipa               -> IPA transcription (generic)
    scientific-name(s)-> biological/scientific name
    x-ilda-url        -> pointer into the ILDA dictionary
    url               -> upstream source URL (nativelanguages.org, wiktionary, etc.)
    book-isbn         -> print source ISBN
    x-letter          -> dictionary letter/alphabetical grouping
    x-form-type       -> stem | word | etc.
    pos               -> part of speech (noun, verb, ...)

Usage:
    python3 tmx_to_xliff2.py input.tmx output.xliff --src en --tgt mia

    # batch mode, same behavior as the original script:
    python3 tmx_to_xliff2.py --batch /path/to/dir --src en --tgt mia
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET

XLIFF_NS = "urn:oasis:names:tc:xliff:document:2.0"
MDA_NS = "urn:oasis:names:tc:xliff:metadata:2.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"

ET.register_namespace("", XLIFF_NS)
ET.register_namespace("mda", MDA_NS)

# Known prop-type -> friendlier metaGroup category, purely cosmetic/organizational.
PROP_CATEGORY = {
    "x-ipa-mia": "pronunciation",
    "ipa": "pronunciation",
    "scientific-name": "taxonomy",
    "scientific names": "taxonomy",
    "x-ilda-url": "source-link",
    "url": "source-link",
    "book-isbn": "bibliographic",
    "x-letter": "dictionary-index",
    "x-form-type": "morphology",
    "pos": "morphology",
}

CTRL_CHARS_TO_STRIP = [f"&#x{i:X};" for i in range(0x00, 0x20) if i not in (0x09, 0x0A, 0x0D)]


def preprocess_tmx_file(file_path):
    """Strip illegal XML control-char entities in place, same as the base script."""
    with open(file_path, "r", encoding="utf-8") as f:
        xml_content = f.read()
    for ent in CTRL_CHARS_TO_STRIP:
        xml_content = xml_content.replace(ent, "")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(xml_content)


def _prop_category(prop_type):
    # Strip an optional "src:"/"tgt:" side-prefix before category lookup,
    # so e.g. "tgt:x-ipa-mia" still lands in "pronunciation".
    bare = prop_type.strip()
    if bare.lower().startswith(("src:", "tgt:")):
        bare = bare.split(":", 1)[1]
    return PROP_CATEGORY.get(bare.lower(), "custom")


def build_metadata_element(props):
    """
    props: list of (type, text) tuples pulled from <prop> elements.
    Returns an <mda:metadata> element grouping props by category,
    or None if there are no props to attach.
    """
    if not props:
        return None

    metadata = ET.Element(f"{{{MDA_NS}}}metadata")
    groups = {}
    for ptype, text in props:
        cat = _prop_category(ptype)
        groups.setdefault(cat, []).append((ptype, text))

    for cat, items in groups.items():
        meta_group = ET.SubElement(
            metadata, f"{{{MDA_NS}}}metaGroup", attrib={"category": cat}
        )
        for ptype, text in items:
            meta = ET.SubElement(meta_group, f"{{{MDA_NS}}}meta", attrib={"type": ptype})
            meta.text = text
    return metadata


def parse_tmx_file(file_path, source_lang, target_lang):
    """
    Parse a TMX file and return a list of translation-unit dicts:
        {
          "source": str,
          "target": str,
          "tu_props": [(type, text), ...],       # shared across both tuv
          "source_props": [(type, text), ...],   # source-tuv-only
          "target_props": [(type, text), ...],   # target-tuv-only
        }
    """
    preprocess_tmx_file(file_path)

    tree = ET.parse(file_path)
    root = tree.getroot()
    ns = {"xml": XML_NS}

    units = []
    for tu in root.findall(".//tu"):
        tu_props = [
            (p.get("type", ""), (p.text or "").strip())
            for p in tu.findall("prop")
        ]

        source_text, source_props = None, []
        target_text, target_props = None, []

        for tuv in tu.findall("tuv"):
            lang = tuv.get(f"{{{XML_NS}}}lang") or tuv.get("lang")
            seg = tuv.find("seg")
            text = (seg.text or "").strip() if seg is not None else ""
            props = [
                (p.get("type", ""), (p.text or "").strip())
                for p in tuv.findall("prop")
            ]

            if lang == source_lang:
                source_text, source_props = text, props
            elif lang == target_lang:
                target_text, target_props = text, props

        if source_text is None or target_text is None:
            # Skip tu entries that don't have both requested languages.
            continue

        units.append(
            {
                "source": source_text,
                "target": target_text,
                "tu_props": tu_props,
                "source_props": source_props,
                "target_props": target_props,
            }
        )

    print(f"Parsed {len(units)} translation units with props preserved.")
    return units


def create_xliff2(units, source_lang, target_lang, original_filename, output_file):
    xliff = ET.Element(
        f"{{{XLIFF_NS}}}xliff",
        attrib={
            "version": "2.2",
            "srcLang": source_lang,
            "trgLang": target_lang,
        },
    )

    file_el = ET.SubElement(
        xliff, f"{{{XLIFF_NS}}}file", attrib={"id": "f1", "original": original_filename}
    )

    for i, unit in enumerate(units, start=1):
        unit_el = ET.SubElement(file_el, f"{{{XLIFF_NS}}}unit", attrib={"id": str(i)})

        # tu-level props apply to the whole unit (both languages)
        unit_meta = build_metadata_element(unit["tu_props"])
        if unit_meta is not None:
            unit_el.append(unit_meta)

        segment_el = ET.SubElement(unit_el, f"{{{XLIFF_NS}}}segment")
        source_el = ET.SubElement(segment_el, f"{{{XLIFF_NS}}}source")
        source_el.text = unit["source"]
        target_el = ET.SubElement(segment_el, f"{{{XLIFF_NS}}}target")
        target_el.text = unit["target"]

        # per-language props: attach as metadata on the segment, tagged by side,
        # since XLIFF 2.2 core doesn't allow mda:metadata directly on source/target.
        side_props = [("src:" + t, v) for t, v in unit["source_props"]] + [
            ("tgt:" + t, v) for t, v in unit["target_props"]
        ]
        side_meta = build_metadata_element(side_props)
        if side_meta is not None:
            unit_el.append(side_meta)

    tree = ET.ElementTree(xliff)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"XLIFF 2.2 file created: {output_file}")


def convert_one(input_path, output_path, source_lang, target_lang):
    units = parse_tmx_file(input_path, source_lang, target_lang)
    create_xliff2(units, source_lang, target_lang, os.path.basename(input_path), output_path)


def main():
    ap = argparse.ArgumentParser(description="Convert TMX (with extended props) to XLIFF 2.2.")
    ap.add_argument("input", nargs="?", help="Input .tmx file (single-file mode)")
    ap.add_argument("output", nargs="?", help="Output .xliff file (single-file mode)")
    ap.add_argument("--batch", metavar="DIR", help="Convert every .tmx file in DIR into DIR/output/")
    ap.add_argument("--src", required=True, help="Source language code, e.g. en")
    ap.add_argument("--tgt", required=True, help="Target language code, e.g. mia")
    args = ap.parse_args()

    if args.batch:
        if not os.path.isdir(args.batch):
            print("Invalid directory.")
            sys.exit(1)
        out_dir = os.path.join(args.batch, "output")
        os.makedirs(out_dir, exist_ok=True)
        for fname in os.listdir(args.batch):
            if fname.endswith(".tmx"):
                in_path = os.path.join(args.batch, fname)
                out_path = os.path.join(
                    out_dir, f"{os.path.splitext(fname)[0]}_{args.src}_{args.tgt}.xliff"
                )
                convert_one(in_path, out_path, args.src, args.tgt)
    else:
        if not args.input or not args.output:
            ap.error("input and output are required unless --batch is used")
        convert_one(args.input, args.output, args.src, args.tgt)


if __name__ == "__main__":
    main()
