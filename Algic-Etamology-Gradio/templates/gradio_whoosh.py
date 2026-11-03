"""
gradio_whoosh.py
A high-performance generic search-anything template using Whoosh and Gradio.
Can be upstreamed or dropped into any pipeline to provide instantaneous text searches.
"""

import os
import shutil
import gradio as gr
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import MultikeywordParser, OrGroup

# 1. Define Global Configuration & Target Search Index Storage directory
INDEX_DIR = "whoosh_index"

# 2. Define a Generic Multi-Field Search Schema
# Documents can have unique IDs, a title/name, and a heavy blob text field
generic_schema = Schema(
    id=ID(stored=True, unique=True),
    title=TEXT(stored=True),
    body=TEXT(stored=True)
)

def initialize_search_index(sample_dataset=None):
    """
    Creates and populates the local Whoosh indexing directory.
    Re-creates the index cleanly if it already exists.
    """
    if os.path.exists(INDEX_DIR):
        shutil.rmtree(INDEX_DIR)
    os.mkdir(INDEX_DIR)
    
    ix = create_in(INDEX_DIR, generic_schema)
    writer = ix.writer()
    
    # If no data is supplied, drop in a sample Algonquian dataset framework as a baseline template
    if sample_dataset is None:
        sample_dataset = [
            {"id": "ats", "title": "Gros Ventre (Aaniiih)", "body": "ISO: ats. Glottocode: gros1243. Group: Plains. Reconstructed ancestral roots with interlinear morphs."},
            {"id": "arp", "title": "Arapaho (Hinónoʼeitíít)", "body": "ISO: arp. Glottocode: arap1280. Group: Plains. Heavily documented morphology and structural syntax parameters."},
            {"id": "bue", "title": "Beothuk (Extinct Isolate)", "body": "ISO: bue. Glottocode: beot1247. Location: Newfoundland. Extinct since 1829. Contains Hewson vocabulary data matrix comparisons."},
            {"id": "crk", "title": "Plains Cree (Nehiyawewin)", "body": "ISO: crk. Glottocode: plai1258. Group: Central / Great Lakes. Highly active modern Algonquian system framework with massive lexicon."},
            {"id": "alg-pro", "title": "Proto-Algonquian Ancestral Reconstruction", "body": "ID: alg-pro. Ultimate macro-etymological source layer for multi-dialect comparative dictionary terms."}
        ]
        
    for doc in sample_dataset:
        writer.add_document(id=doc["id"], title=doc["title"], body=doc["body"])
    
    writer.commit()
    print(f"Whoosh Indexing Engine successfully initialized with {len(sample_dataset)} entries.")

def perform_whoosh_query(query_text):
    """
    Executes a high-speed text parser search against multiple fields.
    """
    if not query_text or query_text.strip() == "":
        return "⚠️ Please type a query into the box above to filter documents."
        
    if not os.path.exists(INDEX_DIR):
        return "❌ Whoosh index directory not initialized. Please call initialize_search_index() first."
        
    ix = open_dir(INDEX_DIR)
    results_payload = []
    
    # Use a MultikeywordParser to check across both 'title' and 'body' fields simultaneously
    # OrGroup allows partial matches to cascade correctly into hits
    parser = MultikeywordParser(["title", "body"], ix.schema, group=OrGroup.factory(0.9))
    parsed_query = parser.parse(query_text)
    
    with ix.searcher() as searcher:
        hits = searcher.search(parsed_query, limit=20)
        
        if len(hits) == 0:
            return f"🔍 Search complete. No documents found matching: **'{query_text}'**"
            
        results_payload.append(f"### 🎉 Found {len(hits)} Matching Document Elements:\n")
        
        for index, hit in enumerate(hits, start=1):
            score = round(hit.score, 3)
            results_payload.append(
                f"#### [{index}] {hit['title']} \n"
                f"* **Document Reference ID:** `{hit['id']}`\n"
                f"* **Search Engine Score Ranking:** `{score}`\n"
                f"* **Text Snippet:** *\"{hit['body']}\"*\n"
                f"---"
            )
            
    return "\n".join(results_payload)

def create_whoosh_search_app():
    """
    Constructs the target Gradio Blocks layout interface window.
    """
    # Initialize index immediately on application startup thread
    initialize_search_index()
    
    with gr.Blocks(theme=gr.themes.Default(primary_hue="teal", radius_size="sm")) as interface:
        gr.Markdown("## ⚡ Fast Whoosh Full-Text Search Anything Template")
        gr.Markdown("A fast lookup framework. Input any search string, key token, or parameter fragment to scan indices.")
        
        with gr.Row():
            with gr.Column(scale=1):
                # Search Box Input Widget
                search_box = gr.Textbox(
                    placeholder="Type to search index instantly (e.g. 'Plains', 'gros1243', '1829')...",
                    label="Search Entry Text Field",
                    max_lines=1
                )
                clear_btn = gr.Button("Clear Panel Inputs", variant="secondary")
                
            with gr.Column(scale=2):
                # Render engine mapping area output
                output_panel = gr.Markdown(
                    value="*Search results context will populate here dynamically...*",
                    label="Index Document Matrix Hits View"
                )
                
        # Connect listeners to execute queries on input or submission events
        search_box.submit(fn=perform_whoosh_query, inputs=search_box, outputs=output_panel)
        search_box.change(fn=perform_whoosh_query, inputs=search_box, outputs=output_panel)
        
        # Reset behavior
        clear_btn.click(fn=lambda: ("", "*Search results context will populate here dynamically...*"), outputs=[search_box, output_panel])
        
    return interface

if __name__ == "__main__":
    # Local runtime initialization block execution
    demo = create_whoosh_search_app()
    demo.launch(server_name="0.0.0.0", server_port=7865)
