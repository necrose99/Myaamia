# Justfile for Myaamia Language RAG System

# Set shell
set shell := ["bash", "-cu"]

# Variables
MODEL_DIR := "~/.ollama"
DATA_DIR := "./data"
SQLITE := "${DATA_DIR}/myaamia.sqlite"

# Install system deps (Debian/Ubuntu)
install-deps:
	sudo apt update
	sudo apt install -y podman sqlite3 python3 python3-pip \
		espeak-ng libespeak-ng-dev build-essential \
		tesseract-ocr poppler-utils curl unzip
	pip3 install -U pip
	pip3 install -r requirements.txt

# Start Ollama and WebUI containers
start-containers:
	podman run -d --name ollama -v ${MODEL_DIR}:/root/.ollama -p 11434:11434 ollama/ollama
	podman run -d --name open-webui --network host -v open-webui-data:/app/backend/data ghcr.io/open-webui/open-webui:main

# Stop containers
stop-containers:
	podman stop ollama || true
	podman stop open-webui || true

# Pull required models for local usage
pull-models:
	ollama pull mistral
	ollama pull phi3
	ollama pull openhermes
	ollama pull llava

# Create empty RAG database with schema
setup-db:
	sqlite3 ${SQLITE} < RAG/rag-sqlite.sql

# Ingest PDFs into RAG DB
ingest-pdf:
	python3 scripts/ingest_pdf.py --input ./PDF_IMPORT/sources --db ${SQLITE}

# Scrape web pages and insert into DB
scrape-web:
	python3 scripts/scrape_site.py --urls urls.txt --db ${SQLITE}

# Convert MP3s to phonemes
phonemes:
	python3 scripts/phoneme_pipeline.py --audio-dir ./PHONEMES/audio --db ${SQLITE}

# Export SQLite to TMX file
export-tmx:
	python3 scripts/export_tmx.py --db ${SQLITE} --output ./exports/myaamia.tmx

# Export training JSONL (OpenAI fine-tune)
export-jsonl:
	python3 scripts/sqlite_to_jsonl.py --db ${SQLITE} --out ./exports/myaamia.jsonl

# Wipe & rebuild database from schema
reset-db:
	rm -f ${SQLITE}
	just setup-db
