# ==============================================================================
# Universal Multi-Platform Algic Justfile Workflow Engine (Win / *nix / macOS)
# ==============================================================================

<<<<<<< Updated upstream
# sniffs system platform properties
=======
>>>>>>> Stashed changes
os-type := os()
app-dir := if path_exists("Etamology-Flask") { "Etamology-Flask" } else { "." }

default: help

<<<<<<< Updated upstream
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
=======
# List all platform-agnostic diagnostic and build pipelines
help:
    @just --list

# ── RAPID BOOTSTRAPPING FOR RESEARCH WORKSTATIONS ──────────────────────────────

# Pull down pre-compiled binary utilities instantly via one-liner toolchain wrappers
bootstrap:
    {{ if os-type == "windows" { "powershell.exe -Command \"Set-ExecutionPolicy Unrestricted -Scope Process; iex (iwr 'https://githubusercontent.com').Content\"" } else { "curl -L --proto '=https' --tlsv1.2 -sSf https://githubusercontent.com | bash" } }}
    @echo "[✔] Toolchain engine installation step completed successfully."

# ── SEAMLESS CROSS-PLATFORM RUN ENGINE (PORT 8181) ────────────────────────────

# Execute dynamic pre-flight compilation check asset and font matrix updates
build-assets:
    hatch run python {{app-dir}}/build.py

# Boot diagnostic loop directly on isolated testing port 8181
run: build-assets
    hatch run python {{app-dir}}/algic_ety_applet_v3.py --port 8181 --host 127.0.0.1 --debug

# ── CX_FREEZE BINARY WORKFLOW ─────────────────────────────────────────────────

# Freeze application binary packages for local diagnostics based on runtime host OS
>>>>>>> Stashed changes
freeze: build-assets
    hatch run python setup.py build
    @echo "[✔] Freezing completed! Output available in the platform target directory within: ./build/"

<<<<<<< Updated upstream
# ── ENGINE CONTAINER HOOKS ───────────────────────────────────────────────────

# Launch container layers safely depending on host capabilities
up:
    {{ if os-type == "windows" { "powershell.exe ./deploy.sh" } else { "./deploy.sh" } }}

# Bring down running cluster states
down:
    {{ if os-type == "windows" { "docker compose down" } else { "docker compose down 2>/dev/null || podman-compose down" } }}
=======
# ── INITIALIZE TESTING ENVIRONMENT (HATCH) ────────────────────────────────────

# Create localized virtual shell workspace environment
init:
    hatch env create
>>>>>>> Stashed changes

# Clean build artifacts, platform temporary files, and __pycache__ trees
clean:
    hatch env prune
    {{ if os-type == "windows" { "powershell.exe -Command \"Remove-Item -Recurse -Force build,dist,**\\__pycache__ -ErrorAction SilentlyContinue\"" } else { "rm -rf build/ dist/ **/__pycache__ *.pyd *.so *.c" } }}
<<<<<<< Updated upstream
    @echo "[✔] Multi-platform cache nodes cleared."
=======
>>>>>>> Stashed changes
