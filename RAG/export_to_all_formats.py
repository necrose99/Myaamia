#!/usr/bin/python3
import subprocess
import os

def export_to_all_formats(model_id, output_path):
    print(f"[*] Starting Export for {model_id}...")

    # 1. Export to ONNX (for Axelera Metis)
    # This uses the RTX 2070 to accelerate the export process
    onnx_path = os.path.join(output_path, "onnx")
    subprocess.run([
        "optimum-cli", "export", "onnx", 
        "--model", model_id, 
        "--task", "text-generation-with-past", 
        onnx_path
    ])

    # 2. Convert to GGUF (for Ollama)
    # Requires llama.cpp cloned in your /home/ollama/data/tools
    gguf_path = os.path.join(output_path, f"{model_id.split('/')[-1]}.gguf")
    subprocess.run([
        "python3", "/home/ollama/data/tools/llama.cpp/convert.py",
        os.path.join(onnx_path), 
        "--outfile", gguf_path,
        "--outtype", "q8_0" 
    ])

    print(f"[+] Export Complete: {gguf_path}")

if __name__ == "__main__":
    models = ["mannix/llamax3-8b-alpaca", "mistralai/Mistral-7B-v0.1"]
    for m in models:
        export_to_all_formats(m, f"/home/ollama/data/models/{m}")
