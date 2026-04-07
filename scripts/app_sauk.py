# !/usr/bin/env python3
"""
Sauk-English translation web app.
"""
import gradio as gr
from transformers import MarianMTModel, MarianTokenizer
import torch

class SaukTranslator:
    def __init__(self, model_path="./sauk-translator"):
        self.model_path = model_path
        self.load_model()
        
    def load_model(self):
        """Load the trained model."""
        try:
            self.model = MarianMTModel.from_pretrained(self.model_path)
            self.tokenizer = MarianTokenizer.from_pretrained(
                "Helsinki-NLP/opus-mt-mul-en"
            )
            print(f"✅ Loaded model from {self.model_path}")
        except:
            # Fallback to pre-trained multilingual model
            print(f"⚠️ Using fallback model")
            self.model = MarianMTModel.from_pretrained(
                "Helsinki-NLP/opus-mt-mul-en"
            )
            self.tokenizer = MarianTokenizer.from_pretrained(
                "Helsinki-NLP/opus-mt-mul-en"
            )
    
    def translate(self, text, direction="sauk->en"):
        """Translate text."""
        if not text.strip():
            return ""
        
        # Set up source and target languages
        if direction == "sauk->en":
            src_lang, tgt_lang = "sauk", "en"
        else:
            src_lang, tgt_lang = "en", "sauk"
        
        # Add language tags if needed (MarianMT handles this automatically)
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            padding=True, 
            truncation=True
        )
        
        # Generate translation
        with torch.no_grad():
            try:
                if torch.cuda.is_available():
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                    outputs = self.model.generate(**inputs)
                else:
                    outputs = self.model.generate(**inputs)
            except Exception as e:
                print(f"Translation error: {e}")
                return "Translation failed"
        
        # Decode
        translation = self.tokenizer.decode(
            outputs[0], 
            skip_special_tokens=True
        )
        
        return translation
    
    def create_app(self):
        """Create Gradio app."""
        with gr.Blocks(title="Sauk Language Helper", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 💚 Sa ki (The Sauk Language)")
            gr.Markdown("A tool for learning and preserving the Sauk language of the Sac and Fox Nation.")
            
            with gr.Row():
                with gr.Column(scale=1):
                    text_input = gr.Textbox(
                        label="Enter text", 
                        placeholder="Type in English or Sauk...",
                        lines=4,
                        optional=False
                    )
                with gr.Column(scale=1):
                    text_output = gr.Textbox(
                        label="Translation", 
                        lines=4,
                        interactive=False
                    )
            
            # Direction selector
            direction = gr.Radio(
                choices=["Sauk → English", "English → Sauk"],
                value="Sauk → English",
                label="Translation Direction"
            )
            
            def translate_wrapper(text, direction):
                lang = "sauk->en" if direction == "Sauk → English" else "en->sauk"
                return self.translate(text, lang)
            
            text_input.submit(translate_wrapper, 
                            inputs=[text_input, direction], 
                            outputs=text_output)
            
            with gr.Row():
                gr.Button("Clear", variant="secondary").click(
                    lambda: ["", ""],
                    inputs=[text_input, text_output],
                    outputs=[text_input, text_output]
                )
            
            gr.Markdown("---")
            gr.Markdown("### 📖 Example Phrases:")
            examples = gr.Examples(
                examples=[
                    ["Hello, how are you?"],
                    ["What is your name?"],
                    ["I love the earth"],
                    ["The sky is blue"],
                    ["Thank you very much"],
                    ["Néka ki?"],  # Example Sauk phrase
                ],
                inputs=text_input,
                label="Try these examples"
            )
            
            gr.Markdown("---")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 📚 Dictionary Data")
                    gr.HTML(f"""
                    <ul>
                    <li><strong>Entries:</strong> {len(pd.read_csv('sauk_dictionary.csv'))}</li>
                    <li><strong>Source:</strong> A Concise Dictionary of Sauk</li>
                    <li><strong>Community:</strong> Sac and Fox Nation</li>
                    </ul>
                    """)
                with gr.Column():
                    gr.Markdown("#### 💡 Usage Tips")
                    gr.HTML("""
                    <ul>
                    <li>Start with simple words and phrases</li>
                    <li>Use for vocabulary building</li>
                    <li>Always verify with fluent speakers</li>
                    <li>This is a learning aid, not a replacement for human teachers</li>
                    </ul>
                    """)
        
        return demo

if __name__ == "__main__":
    translator = SaukTranslator()
    app = translator.create_app()
    app.launch(share=True)  # Get public URL
