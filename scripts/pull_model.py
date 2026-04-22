import os
from huggingface_hub import hf_hub_download

# 1. Setup paths
model_dir = r"C:\Users\black\GitHub\Myaamia\models"
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

# 2. Download specific GGUF file
# We are getting the 4-bit Medium quantization (good balance of speed/smarts)
print("🚀 Starting download of Llama-3-8B (Q4_K_M)...")
model_path = hf_hub_download(
    repo_id="bartowski/Meta-Llama-3-8B-Instruct-GGUF",
    filename="Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
    local_dir=model_dir,
    local_dir_use_symlinks=False
)

print(f"✅ Model downloaded to: {model_path}")