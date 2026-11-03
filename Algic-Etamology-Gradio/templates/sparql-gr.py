import gradio as gr
import sqlite3
import pandas as pd

def query_hover_metadata(search_key):
    """
    Simulates a server hover look up.
    Resolves Glottocode, ISO-639-3, WALS, Wikidata and Ontolex definitions instantly.
    """
    if not search_key:
        return "Please input a valid search parameter (e.g. 'ats', 'crk', 'Beothuk')."
        
    conn = sqlite3.connect("sparql_cache.db")
    cursor = conn.cursor()
    
    # Dynamic parameter binding matching any core attribute identifier safely
    query = """
        SELECT l.display_name, l.glottocode, l.iso_639_3, l.wals_code, l.wikidata_id, l.subfamily_group, e.written_rep, e.morpheme_glos
        FROM languoids l
        LEFT JOIN lexical_entries e ON l.glottocode = e.glottocode
        WHERE l.iso_639_3 = ? OR l.glottocode = ? OR l.display_name LIKE ?
    """
    
    like_pattern = f"%{search_key}%"
    cursor.execute(query, (search_key, search_key, like_pattern))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return f"🚫 No metadata mappings found for token parameter: '{search_key}'"
        
    name, gc, iso, wals, wd, group, lemon_rep, lemon_glos = result
    
    # Return structured markdown string designed for rendering inside frontend UI panels
    markdown_tooltip = f"""
    ### 🌐 {name} Layout Mapping Properties
    * **Glottocode node:** `{gc}`
    * **ISO 639-3 Identifier:** `{iso if iso else 'N/A'}`
    * **WALS Lexicon Code:** `{wals if wals else 'N/A'}`
    * **Genealogical Tree Group:** `{group}`
    * **Wikidata SPARQL Hook:** `wd:{wd}`
    
    ---
    #### 📖 Ontolex-Lemon Lexical Assertion Element
    * **Native Auto-Rep Representation:** `{lemon_rep if lemon_rep else 'Not Documented Natively'}`
    * **Interlinear Morphological Gloss:** *"{lemon_glos if lemon_glos else 'No parsing schema found'}"*
    """
    return markdown_tooltip

# Generating interactive display block
with gr.Blocks(title="Linguistic Etymology Server Engine") as app:
    gr.Markdown("## 🛠️ Unified Linguistic SPARQL/SQLite Hover Client Engine")
    gr.Markdown("Acts as an ingestion server mapping local TMX/TBX terminology records directly to dynamic Glottolog/Ontolex indices.")
    
    with gr.Row():
        with gr.Column(scale=1):
            input_token = gr.Textbox(placeholder="Enter ISO key, Glottocode, or name (e.g. 'ats', 'bue', 'Arapaho')", label="Search Entity Target")
            submit_btn = gr.Button("Query Local DB Index", variant="primary")
        with gr.Column(scale=2):
            output_hover_panel = gr.Markdown(label="Hydrated Metadata Toolkit Hover Display Context")
            
    submit_btn.click(fn=query_hover_metadata, inputs=input_token, outputs=output_hover_panel)

if __name__ == "__main__":
    app.launch()
