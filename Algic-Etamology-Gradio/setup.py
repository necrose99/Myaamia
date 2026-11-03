import sys
import os
from pathlib import Path
from cx_Freeze import setup, Executable

# Universal cross-platform path mapping helper
base_dir = Path(__file__).resolve().parent
static_src = base_dir / "Etamology-Flask" / "static"
xslt_src = base_dir / "Etamology-Flask" / "xslt"

# Fail-safe check for building inside isolated container/submodule checkouts
if not static_src.exists():
    static_src = base_dir / "static"
if not xslt_src.exists():
    xslt_src = base_dir / "xslt"

build_exe_options = {
    "packages": ["flask", "rdflib", "sqlite_zstd", "requests", "lxml", "bs4", "fontTools", "saxonche"],
    "include_files": [
        (str(static_src), "static"),
        (str(xslt_src), "xslt"),
    ],
    "excludes": ["tkinter", "unittest", "pydoc", "pdb"],
    "optimize": 2
}

# Native Platform Sniffing Matrix for Diagnostics
base = None
target_extension = ""

if sys.platform == "win32":
    base = "Console" # Forces diagnostic output visibility on Windows hosts
    target_extension = ".exe"
elif sys.platform == "darwin":
    # macOS specific diagnostic configuration adjustments can be mapped here
    pass

setup(
    name="AlgicEtymologyApplet",
    version="3.0.0",
    description="Algic Cross-Platform Diagnostic Compilation Engine",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "Etamology-Flask/algic_ety_applet_v3.py" if (base_dir / "Etamology-Flask").exists() else "algic_ety_applet_v3.py",
            base=base,
            target_name=f"AlgicEtymologyApplet{target_extension}"
        )
    ]
)
