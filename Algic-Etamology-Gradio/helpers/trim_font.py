# helpers/trim_font.py
import os
import sys
from pathlib import Path
from fontTools.subset import main as subsetter

def execute_subset_pipeline(static_dir: str):
    static_path = Path(static_dir)
    print(f"Executing web-font matrix build inside: {static_path.resolve()}")
    
    # 1. Bypassing Catrinity GPOS Malformed Bounds Bug
    catrinity_file = static_path / "Catrinity.otf"
    if catrinity_file.exists():
        out_glas = static_path / "Catrinity-GLAS.woff2"
        print("-> Re-indexing Archival GLAS matrix boundaries...")
        try:
            subsetter([
                str(catrinity_file),
                "--unicodes=U+0000-007F,U+E480-E4BF", # Private Use Area (PUA) Mapping Frame
                f"--output-file={str(out_glas)}",
                "--flavor=woff2",
                "--layout-features=", # Blank layout bypasses GPOS table corruption boundary perfectly
                "--glyph-names",
                "--no-hinting",
                "--ignore-missing-glyphs"
            ])
            print("   ✔ Successfully packed web asset: Catrinity-GLAS.woff2")
        except Exception as e:
            print(f"   [!] Catrinity extraction error isolation: {e}")
            
    # 2. Process Native Dialect Stacks (Noto Sans & BJCree weights)
    unicode_map = {
        "Cree": "U+0000-007F,U+1400-167F,U+18B0-18FF",
        "Cherokee": "U+0000-007F,U+13A0-13FF,U+AB70-ABBF"
    }
    
    for font_bin in static_path.glob("*.[ot][tt]f"):
        name_lower = font_bin.name.lower()
        
        # Skip intermediate targets or base Catrinity file
        if "glas" in name_lower or name_lower == "catrinity.otf" or font_bin.suffix == ".woff2":
            continue
            
        target_range = None
        if "cree" in name_lower or "canadian" in name_lower:
            target_range = unicode_map["Cree"]
        elif "cherokee" in name_lower:
            target_range = unicode_map["Cherokee"]
            
        if target_range:
            # Preserves target weight identities natively (e.g. NotoSansCherokee-Bold.woff2)
            out_file = font_bin.with_suffix(".woff2")
            print(f"-> Extracting structural constraints for [{font_bin.name}]...")
            try:
                subsetter([
                    str(font_bin),
                    f"--unicodes={target_range}",
                    f"--output-file={str(out_file)}",
                    "--flavor=woff2",
                    "--layout-features=kern,liga,calt", # Preserve connections for authentic script rendering
                    "--glyph-names",
                    "--no-hinting",
                    "--ignore-missing-glyphs"
                ])
                print(f"   ✔ Generated weight file asset: {out_file.name}")
            except Exception as e:
                print(f"   [!] Skipping structural error on [{font_bin.name}]: {e}")

if __name__ == "__main__":
    TARGET_PATH = r"C:\Users\black\GitHub\Myaamia\Algic-Etamology-Flask\static"
    if not os.path.exists(TARGET_PATH):
        TARGET_PATH = str(Path(__file__).parent.parent / "static")
        
    execute_subset_pipeline(TARGET_PATH)
