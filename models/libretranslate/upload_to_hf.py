
#!/usr/bin/env python3
import os
from huggingface_hub import HfApi

def upload_myaamia_assets():
    repo_id = "necrose99/en_mia.argosmodel"
    # Current folder: C:\Users\black\GitHub\Myaamia\models\libretranslate
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Parent folder: C:\Users\black\GitHub\Myaamia\models
    parent_dir = os.path.dirname(current_dir)
    
    api = HfApi()
    print(f"[-] Starting upload sequence to Hugging Face: {repo_id}")
    
    # 1. Upload the finalized compiled distribution package
    compiled_model = os.path.join(parent_dir, "en_mia.argosmodel")
    if os.path.exists(compiled_model):
        print(f"[~] Uploading compiled distribution asset: en_mia.argosmodel...")
        api.upload_file(
            path_or_fileobj=compiled_model,
            path_in_repo="en_mia.argosmodel",
            repo_id=repo_id,
            repo_type="model"
        )
    else:
        print(f"[!] Warning: Could not find compiled model package at: {compiled_model}")

    # 2. Upload the raw backend model matrix
    model_bin = os.path.join(current_dir, "model", "model.bin")
    if os.path.exists(model_bin):
        print(f"[~] Uploading 44MB quantized Transformer matrix...")
        api.upload_file(
            path_or_fileobj=model_bin,
            path_in_repo="model/model.bin",
            repo_id=repo_id,
            repo_type="model"
        )

    # 3. Upload the vocabulary tracking file
    shared_vocab = os.path.join(current_dir, "model", "shared_vocabulary.json")
    if os.path.exists(shared_vocab):
        print(f"[~] Uploading shared_vocabulary.json map...")
        api.upload_file(
            path_or_fileobj=shared_vocab,
            path_in_repo="model/shared_vocabulary.json",
            repo_id=repo_id,
            repo_type="model"
        )

    print("[+] Complete! Your translation artifacts are now fully updated and live on Hugging Face.")

if __name__ == "__main__":
    upload_myaamia_assets()
