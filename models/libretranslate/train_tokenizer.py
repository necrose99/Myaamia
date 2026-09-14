#!/usr/bin/env python3
import os
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace

def train_myaamia_tokenizer():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_text = os.path.join(base_dir, "myaamia_pairs.txt")
    output_model = os.path.join(base_dir, "myaamia_tokenizer.json")
    
    if not os.path.exists(input_text):
        print(f"[!] Error: Clean training rows missing at: {input_text}")
        return

    print("[-] Compiling token matrix via tokenizers BPE training loop...")
    
    # Initialize a Byte-Pair Encoding model with an Unknown token fallback
    tokenizer = Tokenizer(BPE(unk_token="<unk>"))
    tokenizer.pre_tokenizer = Whitespace()

    # Configure trainer matching your original parameters
    trainer = BpeTrainer(
        vocab_size=4000, 
        special_tokens=["<pad>", "<s>", "</s>", "<unk>"],
        initial_alphabet=[] # Natively absorbs unique glyph structures and phonetic signs
    )

    # Train model directly on your text file
    tokenizer.train([input_text], trainer)
    
    # Save the output configuration blueprint
    tokenizer.save(output_model)
    print(f"[+] Tokenizer generated successfully at: {output_model}")

if __name__ == "__main__":
    train_myaamia_tokenizer()

