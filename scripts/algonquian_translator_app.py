# algonquian_translator_app.py
import gradio as gr
import torch
from transformers import MarianMTModel, MarianTokenizer

class AlgonquianTranslator:
    def __init__(self, model_path="./algonquian-multilingual"):
        self.model = MarianMTModel.from_pretrained(model_path)
        self.tokenizer = MarianTokenizer.from_pretrained(model_path)
        
    def translate(self, text, source_lang, target_lang):
        """Translate between any Algonquian language and English."""
        if not text.strip():
            return ""
        
        # Map language names to codes
        lang_map = {
            "Miami-Illinois": "mia",
            "Sauk": "sauk",
            "Meskwaki": "sac",
            "Fox": "sac",
            "Kickapoo": "kic",
            "Shawnee": "sha",
            "Menominee": "men",
            "Cree": "cre",
            "Swampy Cree": "csw",
            "Southern East Cree": "crj",
            "Atikamekw": "atj",
            "Potawatomi": "pot",
            "Ojibwe": "oji",
            "Ottawa": "otw",
            "Chippewa": "ciw",
            "Blackfoot": "bft",
            "Arapaho": "arp",
            "Gros Ventre": "ats",
            "Cheyenne": "chy",
            "Mi'kmaq": "mic",
            "Western Abenaki": "abe",
            "Eastern Abnaki": "aaq",
            "Maliseet-Passamaquoddy": "mal",
            "Mohegan-Pequot": "moo",
            "Munsee": "mua",
            "Unami": "unm",
            "English": "en"
        }
        
        src_code = lang_map.get(source_lang, "en")
        tgt_code = lang_map.get(target_lang, "en")
        
        # Add language tags
        if src_code != "en":
            src = f"<{src_code}>{text}"
        else:
            src = text
            
        if tgt_code != "en":
            tgt_tag = f"<{tgt_code}>"
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
        if tgt_code != "en":
            translation = translation.replace(tgt_tag, "")
        
        return translation.strip()

class AlgonquianApp:
    def __init__(self, translator):
        self.translator = translator
        
    def create_interface(self):
        with gr.Blocks(title="Algonquian Language Helper", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 🌿 Algonquian Language Family")
            gr.Markdown("Translation between 24 Algonquian languages and English")
            
            with gr.Row():
                with gr.Column(scale=1):
                    text_input = gr.Textbox(
                        label="Enter text", 
                        placeholder="Type in any Algonquian language or English...",
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
                choices=["Auto Detect"] + sorted([
                    "Miami-Illinois", "Sauk", "Meskwaki", "Fox", "Kickapoo",
                    "Shawnee", "Menominee", "Cree", "Swampy Cree", "Southern East Cree",
                    "Atikamekw", "Potawatomi", "Ojibwe", "Ottawa", "Chippewa",
                    "Blackfoot", "Arapaho", "Gros Ventre", "Cheyenne",
                    "Mi'kmaq", "Western Abenaki", "Eastern Abnaki", "Maliseet-Passamaquoddy",
                    "Mohegan-Pequot", "Munsee", "Unami", "English"
                ]),
                value="Auto Detect",
                label="Source Language"
            )
            
            target_lang = gr.Dropdown(
                choices=sorted([
                    "English", "Miami-Illinois", "Sauk", "Meskwaki", "Fox",
                    "Kickapoo", "Shawnee", "Menominee", "Cree", "Swampy Cree",
                    "Southern East Cree", "Atikamekw", "Potawatomi", "Ojibwe",
                    "Ottawa", "Chippewa", "Blackfoot", "Arapaho", "Gros Ventre",
                    "Cheyenne", "Mi'kmaq", "Western Abenaki", "Eastern Abnaki",
                    "Maliseet-Passamaquoddy", "Mohegan-Pequot", "Munsee", "Unami"
                ]),
                value="English",
                label="Target Language"
            )
            
            def translate(text, src_lang, tgt_lang):
                # Auto-detect source language (simplified)
                if src_lang == "Auto Detect":
                    # In reality, you'd use a language detector
                    src_code = None
                else:
                    src_code = None  # Placeholder
                
                return self.translator.translate(
                    text, 
                    source_lang=src_lang,
                    target_lang=tgt_lang
                )
            
            text_input.submit(
                translate, 
                inputs=[text_input, source_lang, target_lang], 
                outputs=text_output
            )
            
            with gr.Row():
                gr.Button("Clear", variant="secondary").click(
                    lambda: ["", "Auto Detect", "English", ""],
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
                    ["Hello", "English", "Ojibwe"],
                    ["Thank you", "English", "Cree"],
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
                    <li><strong>Family:</strong> Algonquian</li>
                    <li><strong>Branches:</strong> Plains, Central, Eastern</li>
                    <li><strong>Languages:</strong> 24</li>
                    <li><strong>Focus:</strong> Miami-Illinois & Sauk</li>
                    </ul>
                    """)
                with gr.Column():
                    gr.Markdown("#### 💡 Language Facts")
                    gr.HTML("""
                    <ul>
                    <li>Shared linguistic features</li>
                    <li>Polysynthetic morphology</li>
                    <li>Revitalization efforts</li>
                    <li>Cultural preservation</li>
                    </ul>
                    """)
        
        return demo
