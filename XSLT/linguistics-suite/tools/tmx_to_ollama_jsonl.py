#!/usr/bin/env python3
"""
tmx_to_ollama_jsonl.py
Converts Myaamia (or any Algonquian) TMX files to
Ollama/llama.cpp Alpaca-format fine-tuning JSONL.
Merges multiple TMX files, deduplicates, generates
forward/reverse/identification training pairs.

Usage:
  python tmx_to_ollama_jsonl.py *.tmx --src mia --tgt en
  python tmx_to_ollama_jsonl.py Myaamia-lda-dictionary.tmx \
         myaamia-bundle.tmx --src mia --tgt en \
         --output myaamia_finetune.jsonl
"""
import glob, json, sys, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'bindings'))
import tmx14_ds

def merge(tmx_paths, src_lang, tgt_lang, output, dedup=True):
    seen, total = set(), 0
    with open(output, 'w', encoding='utf-8') as fh:
        for path in tmx_paths:
            try:
                root = tmx14_ds.parse(path, silence=True)
            except Exception as e:
                print(f"Skip {path}: {e}"); continue
            for tu in root.get_body().get_tu():
                tuvs = tu.get_tuv()
                def get(lang):
                    return next((t for t in tuvs if
                        t.get_anyAttributes_().get('lang','')
                        .lower().startswith(lang.lower())), None)
                sv = get(src_lang); tv = get(tgt_lang)
                if not sv or not tv: continue
                src = (sv.get_seg() or '').strip()
                tgt = (tv.get_seg() or '').strip()
                if not src or not tgt: continue
                key = (src.lower(), tgt.lower())
                if dedup and key in seen: continue
                seen.add(key)
                lang_name = 'Myaamia (Miami-Illinois)' \
                    if src_lang == 'mia' else src_lang.upper()
                for inst, inp, out in [
                    (f"Translate the following {lang_name} text to English.",
                     src, tgt),
                    (f"Translate the following English text to {lang_name}.",
                     tgt, src),
                    ("Identify this language and give the English meaning.",
                     src, f"{lang_name}. English: {tgt}"),
                ]:
                    fh.write(json.dumps(
                        {"instruction": inst, "input": inp, "output": out},
                        ensure_ascii=False) + '\n')
                    total += 1
    print(f"Wrote {len(seen)} unique TUs → {total} pairs → {output}")
    return total

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('tmx', nargs='+')
    ap.add_argument('--src',    default='mia')
    ap.add_argument('--tgt',    default='en')
    ap.add_argument('--output', default='finetune.jsonl')
    ap.add_argument('--no-dedup', action='store_true')
    args = ap.parse_args()
    files = []
    for pat in args.tmx:
        files.extend(glob.glob(pat))
    print(f"Processing {len(files)} TMX files...")
    merge(files, args.src, args.tgt, args.output, not args.no_dedup)
