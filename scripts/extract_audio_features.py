# extract_features.py

import os
import json
import librosa
import torch
import numpy as np
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

def process_audio_directory(audio_dir, output_jsonl):
    # 1. Automatically detect and assign GPU device
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"🚀 Using NVIDIA GPU Acceleration: {torch.cuda.get_device_name(0)}")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps") # Mac Silicon fallback
        print("🚀 Using Apple Silicon GPU Acceleration")
    else:
        # Check for DirectML (AMD/Intel on Windows) if torch-directml is installed
        try:
            import torch_directml
            device = torch_directml.device()
            print("🚀 Using AMD/Intel DirectML GPU Acceleration")
        except ImportError:
            device = torch.device("cpu")
            print("⚠️ GPU not detected or unsupported. Falling back to CPU.")

    print("Initializing Universal Phoneme Processor...")
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-xlsr-53-phoneme")
    # Load model and immediately push its weights onto the designated GPU
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-xlsr-53-phoneme").to(device)
    
    TARGET_SR = 16000 
    supported_exts = ('.mp3', '.wav', '.m4a', '.ogg')
    
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for root, _, files in os.walk(audio_dir):
            for file in files:
                if file.lower().endswith(supported_exts):
                    file_path = os.path.join(root, file)
                    print(f"Processing: {file}")
                    
                    try:
                        # 2. Extract Acoustic Timbre & Features (Runs on CPU via librosa)
                        y, sr = librosa.load(file_path, sr=TARGET_SR)
                        duration = float(librosa.get_duration(y=y, sr=sr))
                        
                        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                        mfcc_means = [float(v) for v in np.mean(mfccs, axis=1)]
                        
                        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
                        valid_pitches = pitches[pitches > 0]
                        avg_pitch = float(np.mean(valid_pitches)) if len(valid_pitches) > 0 else 0.0
                        
                        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
                        avg_centroid = float(np.mean(centroid))
                        
                        # 3. Tokenize and push tensor data to the GPU
                        input_features = processor(y, return_tensors="pt", sampling_rate=TARGET_SR)
                        input_values = input_features.input_values.to(device)
                        
                        # 4. Fast GPU Inference
                        with torch.no_grad():
                            logits = model(input_values).logits
                        
                        predicted_ids = torch.argmax(logits, dim=-1)
                        # Move result back to CPU to decode into clean text
                        ipa_text = processor.batch_decode(predicted_ids.cpu())
                        
                        record = {
                            "file_name": file,
                            "ipa_sequence": ipa_text[0] if ipa_text else "",
                            "duration_sec": round(duration, 3),
                            "timbre": {
                                "pitch_f0_hz": round(avg_pitch, 2),
                                "spectral_brightness": round(avg_centroid, 2),
                                "mfcc_signature": [round(x, 4) for x in mfcc_means]
                            }
                        }
                        
                        f.write(json.dumps(record, ensure_ascii=False) + "\n")
                        
                        # Clear VRAM cache periodically to maintain stable 8GB headroom
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                            
                    except Exception as e:
                        print(f"❌ Error skipping file {file}: {str(e)}")

if __name__ == "__main__":
    audio_folder = "./audio_inputs" 
    output_file = "./dataset.jsonl"
    
    if os.path.exists(audio_folder):
        process_audio_directory(audio_folder, output_file)
    else:
        print(f"Error: Target directory '{audio_folder}' does not exist.")
