#!/usr/bin/env python3
import os
import sentencepiece as spm

base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "sentencepiece.model")

print(f"[-] Target File: {model_path}")
if not os.path.exists(model_path):
    print("[!] Verification failed: The file does not exist at this path.")
else:
    file_size = os.path.getsize(model_path)
    print(f"[-] Checked File Size: {file_size} bytes")
    
    try:
        # Attempt to load the model binary configuration into memory
        sp = spm.SentencePieceProcessor()
        sp.load(model_path)
        print("[+] SUCCESS: The SentencePiece engine successfully initialized the model!")
        print(f"[-] Total pieces in matrix vocabulary: {len(sp)}")
    except Exception as e:
        print(f"[!] CRITICAL ERROR: The binary structure is corrupted.\nDetails: {e}")
