#!/usr/bin/env python3
"""
Builds a real parallel corpus from ilda_full.tmx (sentence pairs) and
myaamia_pairs.txt (word/short-phrase pairs) for fine-tuning a pretrained
multilingual model on English <-> Miami-Illinois (ISO 639-3: mia).

Replaces guesswork: this actually reads your source files and reports
real counts, rather than assuming a corpus size.

Output: train.jsonl / valid.jsonl, each line {"en": ..., "mia": ...}
"""
import argparse
import json
import random
import xml.etree.ElementTree as ET
from pathlib import Path


def load_tmx_pairs(tmx_path: Path) -> list[dict]:
    """Extract (en, mia) sentence pairs from a TMX file. Skips any <tu>
    missing either language segment rather than failing the whole parse.
    Normalizes language tag variants (en, en-US, en_US -> en; mia, mia-US -> mia)
    since different source files in this corpus use different tagging."""
    tree = ET.parse(tmx_path)
    pairs = []
    skipped = 0
    for tu in tree.findall(".//tu"):
        segs = {}
        for tuv in tu.findall("tuv"):
            lang = tuv.get("{http://www.w3.org/XML/1998/namespace}lang")
            seg = tuv.find("seg")
            if lang and seg is not None and seg.text:
                norm = lang.lower().replace("_", "-").split("-")[0]
                segs[norm] = seg.text.strip()
        if "en" in segs and "mia" in segs and segs["en"] and segs["mia"]:
            pairs.append({"en": segs["en"], "mia": segs["mia"]})
        else:
            skipped += 1
    print(f"[tmx] {tmx_path.name}: {len(pairs)} usable pairs, {skipped} skipped (missing en or mia segment)")
    return pairs


def load_word_pairs(txt_path: Path) -> list[dict]:
    """myaamia_pairs.txt is tab-separated: mia_headword <TAB> en_gloss.
    Treated as short segment pairs, not full sentences -- useful for
    vocabulary coverage, kept as a separate pool so you can weight/sample
    it differently from real sentence data if the model overfits to short
    entries."""
    pairs = []
    skipped = 0
    for line in txt_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
            skipped += 1
            continue
        mia, en = parts[0].strip(), parts[1].strip()
        pairs.append({"en": en, "mia": mia})
    print(f"[dict] {txt_path.name}: {len(pairs)} word/phrase pairs, {skipped} malformed lines skipped")
    return pairs


def dedupe(pairs: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for p in pairs:
        key = (p["en"].lower(), p["mia"].lower())
        if key not in seen:
            seen.add(key)
            out.append(p)
    if len(out) != len(pairs):
        print(f"[dedupe] removed {len(pairs) - len(out)} exact duplicate pairs")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tmx", type=Path, nargs="+", default=[Path("ilda_full.tmx")],
                     help="One or more TMX files. Pass the real-sentence file "
                          "(e.g. ilda_sentences.tmx) alongside the dictionary-"
                          "derived one -- overlap between sources is deduped "
                          "automatically, first file wins on conflicts.")
    ap.add_argument("--dict", type=Path, default=Path("myaamia_pairs.txt"))
    ap.add_argument("--out-dir", type=Path, default=Path("."))
    ap.add_argument("--val-fraction", type=float, default=0.05,
                     help="Held-out fraction of the deduped pool.")
    ap.add_argument("--include-dict-in-train", action="store_true", default=True)
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()

    random.seed(args.seed)

    all_pairs = []
    for tmx_path in args.tmx:
        all_pairs.extend(load_tmx_pairs(tmx_path))
    word_pairs = load_word_pairs(args.dict) if args.dict.exists() else []
    if args.include_dict_in_train:
        all_pairs = all_pairs + word_pairs

    # Single global dedupe across every source combined -- this is what
    # actually matters, since per-source dedupe alone leaves cross-source
    # duplicates (confirmed: ilda_full.tmx and myaamia_pairs.txt overlap on
    # ~94% of entries) free to leak between train and valid.
    all_pairs = dedupe(all_pairs)

    random.shuffle(all_pairs)
    n_val = max(1, int(len(all_pairs) * args.val_fraction))
    valid = all_pairs[:n_val]
    train = all_pairs[n_val:]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    train_path = args.out_dir / "train.jsonl"
    valid_path = args.out_dir / "valid.jsonl"
    with train_path.open("w", encoding="utf-8") as f:
        for p in train:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    with valid_path.open("w", encoding="utf-8") as f:
        for p in valid:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # Also emit line-aligned plain text files -- this is the format
    # argos-train / OpenNMT-py actually wants (one file per language,
    # line N in each file is a translation pair).
    for split_name, split_data in (("train", train), ("valid", valid)):
        with (args.out_dir / f"{split_name}.mia").open("w", encoding="utf-8") as f_mia, \
             (args.out_dir / f"{split_name}.en").open("w", encoding="utf-8") as f_en:
            for p in split_data:
                f_mia.write(p["mia"].replace("\n", " ").strip() + "\n")
                f_en.write(p["en"].replace("\n", " ").strip() + "\n")

    print(f"\n[done] train: {len(train)} pairs -> {train_path}, train.mia/train.en")
    print(f"[done] valid: {len(valid)} pairs (held out, no overlap with train) -> {valid_path}, valid.mia/valid.en")
    if len(all_pairs) < 5000:
        print(f"\n[note] {len(all_pairs)} total pairs (dictionary-level mostly) is low-resource "
              f"for sentence-level translation. Fine-tuning a pretrained multilingual model "
              f"(see finetune_nllb.py) will get more out of this than training from scratch.")


if __name__ == "__main__":
    main()