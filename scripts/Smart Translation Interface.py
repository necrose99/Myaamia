import gradio as gr

class AlgicTranslator:
    def __init__(self, model_path="./algic-multilingual"):
        self.model = MarianMTModel.from_pretrained(model_path)
        self.tokenizer = MarianTokenizer.from_pretrained(model_path)
        
    def translate(self, text, source_lang, target_lang):
        """Translate between any Algic language and English."""
        if not text.strip():
            return ""
        
        # Map language names to codes
        lang_map = {
            "Miami-Illinois": "mia",
            "Sauk": "sauk",
            "English": "en"
        }
        
        src_code = lang_map[source_lang]
        tgt_code = lang_map[target_lang]
        
        # Add language tags
        if src_code == "mia":
            src = f"<mia>{text}"
        elif src_code == "sauk":
            src = f"<sauk>{text}"
        else:
            src = text
            
        if tgt_code == "mia":
            tgt_tag = "<mia>"
        elif tgt_code == "sauk":
            tgt_tag = "<sauk>"
        else:
            tgt_tag = "<en>"
        
        # Tokenize
        inputs = self.tokenizer(
            src, 
            return_tensors="pt", 
            padding=True, 
            truncation=True
        )
        
        # Generate
        with torch.no_grad():
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
                outputs = self.model.generate(**inputs)
            else:
                outputs = self.model.generate(**inputs)
        
        # Decode
        translation = self.tokenizer.decode(
            outputs[0], 
            skip_special_tokens=True
        )
        
        # Remove target tag
        if tgt_code in ["mia", "sauk"]:
            translation = translation.replace(tgt_tag, "")
        
        return translation.strip()

class AlgicApp:
    def __init__(self, translator):
        self.translator = translator
        
    def create_interface(self):
        with gr.Blocks(title="Algic Language Helper", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 🌿 Algic Language Family")
            gr.Markdown("Translation between Miami-Illinois, Sauk, and English")
            
            with gr.Row():
                with gr.Column(scale=1):
                    text_input = gr.Textbox(
                        label="Enter text", 
                        placeholder="Type in any Algic language or English...",
                        lines=4
                    )
                with gr.Column(scale=1):
                    text_output = gr.Textbox(
                        label="Translation", 
                        lines=4,
                        interactive=False
                    )
            
            # Language selection
            source_lang = gr.Dropdown(
                choices=["Auto", "Miami-Illinois", "Sauk", "English"],
                value="Auto",
                label="Source Language"
            )
            
            target_lang = gr.Dropdown(
                choices=["English", "Miami-Illinois", "Sauk"],
                value="English",
                label="Target Language"
            )
            
            def translate(text, src_lang, tgt_lang):
                # Map to internal codes
                lang_map = {
                    "Miami-Illinois": "mia",
                    "Sauk": "sauk",
                    "English": "en",
                    "Auto": None
                }
                
                src_code = lang_map[src_lang]
                tgt_code = lang_map[tgt_lang]
                
                return self.translator.translate(
                    text, 
                    source_lang=src_code,
                    target_lang=tgt_code
                )
            
            text_input.submit(
                translate, 
                inputs=[text_input, source_lang, target_lang], 
                outputs=text_output
            )
            
            with gr.Row():
                gr.Button("Clear", variant="secondary").click(
                    lambda: ["", "Auto", "English", ""],
                    inputs=[text_input, source_lang, target_lang, text_output],
                    outputs=[text_input, source_lang, target_lang, text_output]
                )
            
            gr.Markdown("---")
            gr.Markdown("### 📖 Example Phrases:")
            examples = gr.Examples(
                examples=[
                    ["Neehpennee", "Miami-Illinois", "English"],  # Hello
                    ["Néka ki?", "Sauk", "English"],            # How are you?
                    ["I love the earth", "English", "Miami-Illinois"],
                    ["The sky is beautiful", "English", "Sauk"],
                ],
                inputs=[text_input, source_lang, target_lang],
                label="Try these examples"
            )
            
            gr.Markdown("---")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 📚 Language Data")
                    gr.HTML(f"""
                    <ul>
                    <li><strong>Miami-Illinois:</strong> {len(mia_df)} entries</li>
                    <li><strong>Sauk:</strong> {len(sauk_df)} entries</li>
                    <li><strong>TMX Parallel Sentences:</strong> {len(df_tmx)} pairs</li>
                    <li><strong>Total Training Data:</strong> {len(unified_df)} sentences</li>
                    </ul>
                    """)
                with gr.Column():
                    gr.Markdown("#### 💡 Language Facts")
                    gr.HTML("""
                    <ul>
                    <li>Both are Algonquian languages</li>
                    <li>Share ~30% vocabulary</li>
                    <li>Polysynthetic morphology</li>
                    <li>Revitalization in progress</li>
                    </ul>
                    """)
        
        return demo
