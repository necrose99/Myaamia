from fontTools.subset import main as subsetter

# Define your custom "GLAS" subset parameters
# Includes Basic Latin and the specific Catrinity GLAS PUA range
input_file = "Catrinity.otf"
output_file = "Catrinity-GLAS.woff2"
unicodes = "U+0000-007F,U+E480-E4BF"

# Run the subsetter programmatically
subsetter([
    input_file,
    f"--unicodes={unicodes}",
    "--flavor=woff2",
    f"--output-file={output_file}",
    "--layout-features=kern,liga,calt", # Essential for cursive connections
    "--glyph-names",
    "--no-hinting" # Optional: further reduces file size
])

print(f"Successfully created {output_file}")
