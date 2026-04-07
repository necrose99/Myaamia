# Save this as launch_miami.py
"""
Miami-Illinois Language Revitalization - One-Click Launcher
"""
import argparse
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Launch Miami-Illinois language tools')
    parser.add_argument('--step', type=int, choices=[1,2,3,4,5,6], 
                       default=6, help='Step to run (1=preprocess, 2=train, 3=app, 4=all, 5=hf, 6=arcee)')
    parser.add_argument('--tmx', type=str, default='data/dictionary.tmx',
                       help='Path to TMX file')
    parser.add_argument('--model', type=str, default='arcee/ai-miami-base',
                       help='Model to use (arcee/ai-miami-base or Helsinki-NLP/opus-mt-mul-en)')
    args = parser.parse_args()
    
    # Create necessary directories
    Path("data").mkdir(exist_ok=True)
    Path("models").mkdir(exist_ok=True)
    Path("src").mkdir(exist_ok=True)
    
    if args.step in [1, 4, 6]:
        print("🔧 Step 1: Preprocessing TMX file...")
        subprocess.run([
            "python", "src/preprocess_tmx.py",
            args.tmx,
            "--output-dir", "data"
        ], check=True)
    
    if args.step in [2, 4, 6]:
        print("🤖 Step 2: Training model...")
        if args.model.startswith('arcee'):
            subprocess.run([
                "python", "src/train_model.py",
                "--model-name", args.model,
                "--epochs", "50"
            ], check=True)
        else:
            subprocess.run([
                "python", "src/train_model.py",
                "--model-name", args.model,
                "--epochs", "30"
            ], check=True)
    
    if args.step in [3, 4, 6]:
        print("🌐 Step 3: Launching web app...")
        subprocess.run(["python", "src/app.py"], check=True)
    
    if args.step == 5:
        print("☁️ Step 5: Submitting to Hugging Face Training Cluster...")
        print("\nRun this command in your terminal:")
        print("  huggingface-cli training submit \\")
        print("    --script train_on_hf.py \\")
        print("    --compute-power FULL_V100_1 \\")
        print("    --model_name Helsinki-NLP/opus-mt-mul-en \\")
        print("    --datasets necrose99/miami-illinois-ami \\")
        print("    --token YOUR_HUGGINGFACE_TOKEN")
    
    if args.step == 6:
        print("☁️ Step 6: Submitting to Arcee AI Training Cluster...")
        print("\nRun this command in your terminal:")
        print("  arcee train submit \\")
        print("    --script train_on_arcee.py \\")
        print("    --compute-power A100_1 \\")
        print("    --model arcee/ai-miami-base \\")
        print("    --datasets necrose99/miami-illinois-ami \\")
        print("    --token YOUR_ARCEE_TOKEN")

if __name__ == "__main__":
    main()
