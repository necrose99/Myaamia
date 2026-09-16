# ==============================================================================
# Universal Multi-Platform Algic Justfile Workflow Engine (Win / *nix / macOS)
# ==============================================================================

# sniffs system platform properties
os-type := os()
app-dir := if path_exists("Etamology-Flask") { "Etamology-Flask" } else { "." }

default: help

# List all platform-agnostic automation hooks
help:
    @just --list

# ── SEAMLESS CROSS-PLATFORM RUN ENGINE (PORT 8181) ────────────────────────────

# Execute dynamic pre-flight compilation check asset updates
build-assets:
    hatch run python {{app-dir}}/build.py

# Boot diagnostic loop directly on Port 8181 (Platform agnostic)
run: build-assets
    hatch run python {{app-dir}}/algic_ety_applet_v3.py --port 8181 --host 127.0.0.1 --debug

# ── FREEZE COMPILATION WORKFLOW MATRIX ────────────────────────────────────────

# Freeze application binary packages for local testing based on runtime host OS
freeze: build-assets
    hatch run python setup.py build
    @echo "[✔] Freezing completed! Output available in the platform target directory within: ./build/"

# ── ENGINE CONTAINER HOOKS ───────────────────────────────────────────────────

# Launch container layers safely depending on host capabilities
up:
    {{ if os-type == "windows" { "powershell.exe ./deploy.sh" } else { "./deploy.sh" } }}

# Bring down running cluster states
down:
    {{ if os-type == "windows" { "docker compose down" } else { "docker compose down 2>/dev/null || podman-compose down" } }}

# Clean build artifacts, platform temporary files, and __pycache__ trees
clean:
    hatch env prune
    {{ if os-type == "windows" { "powershell.exe -Command \"Remove-Item -Recurse -Force build,dist,**\\__pycache__ -ErrorAction SilentlyContinue\"" } else { "rm -rf build/ dist/ **/__pycache__ *.pyd *.so *.c" } }}
    @echo "[✔] Multi-platform cache nodes cleared."
