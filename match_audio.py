import os, sys, json, shutil, pd
from faster_whisper import WhisperModel
from rapidfuzz import process, utils, fuzz
import jellyfish # pip install jellyfish
import gc

# 0. SETUP & HARDWARE OPTIMIZATION
sys.stdout.reconfigure(encoding='utf-8')
LOG_JSON = "match_results.jsonl"
GOLD_CSV = "myaamia_gold_standard.csv" # Ensure this has columns: 'myaamia', 'stem'
AUDIO_DIR = r"C:\Users\black\GitHub\Myaamia\corpus_media\full"
OUTPUT_DIR = r"C:\Users\black\GitHub\Myaamia\corpus_media\identified"

def log_to_json(data):
    with open(LOG_JSON, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

# 1. DATA LOADING & PRE-CACHING (Uses your 32GB RAM)
if not os.path.exists(GOLD_CSV):
    print(f"Error: {GOLD_CSV} not found!"); sys.exit()

df = pd.read_csv(GOLD_CSV)
dictionary = df['myaamia'].dropna().tolist()
# Create a lookup for stems if the column exists, else fallback to full word
stem_map = dict(zip(df['myaamia'], df['stem'])) if 'stem' in df.columns else {w: w for w in dictionary}

# Pre-calculate Phonetic Codes to save CPU time in the loop
print("Pre-calculating phonetic 'sound' codes...")
phonetic_lookup = {word: jellyfish.metaphone(str(word)) for word in dictionary}

# 2. ENSEMBLE SCORING ALGORITHM
def get_ensemble_score(heard, target_word):
    target_stem = str(stem_map.get(target_word, target_word))
    
    # Algorithm A: Root-matching (Partial Ratio looks for stem inside the heard string)
    score_stem = fuzz.partial_ratio(target_stem, heard)
    
    # Algorithm B: Sound-matching (Metaphone)
    heard_meta = jellyfish.metaphone(heard)
    score_meta = 100 if heard_meta == phonetic_lookup.get(target_word) else 0
    
    # Algorithm C: Prefix-heavy (Jaro-Winkler)
    score_jw = jellyfish.jaro_winkler_similarity(heard, target_word) * 100
    
    # Weighted Result: Prioritize Stem (50%) and Sound (30%) over pure spelling (20%)
    return (score_stem * 0.5) + (score_meta * 0.3) + (score_jw * 0.2)

# 3. INITIALIZE MODELS
print("Loading Whisper on CPU (Int8)...")
model = WhisperModel("tiny", device="cpu", compute_type="int8")
myaamia_context = ", ".join(dictionary[:50])

# 4. PROCESSING LOOP
for mp3 in os.listdir(AUDIO_DIR):
    if not mp3.endswith(".mp3"): continue
    mp3_path = os.path.join(AUDIO_DIR, mp3)
    
    try:
        segments, _ = model.transcribe(
            mp3_path, language="en", initial_prompt=f"Myaamia: {myaamia_context}", beam_size=5
        )
        
        heard_text = "".join([s.text for s in segments]).lower().strip()
        clean_guess = "".join(e for e in heard_text if e.isalpha())
        if len(clean_guess) < 3: continue

        # First pass: Get top 5 candidates using fast fuzzy matching
        candidates = process.extract(clean_guess, dictionary, limit=5, processor=utils.default_process)
        
        # Second pass: Re-score top 5 using the Ensemble (Roots + Sound)
        best_word, final_confidence = None, 0
        for word, init_score, idx in candidates:
            ens_score = get_ensemble_score(clean_guess, word)
            if ens_score > final_confidence:
                final_confidence = ens_score
                best_word = word

        # 5. LOGGING & FILING
        result = {"file": mp3, "heard": clean_guess, "matched": best_word, "confidence": round(final_confidence, 2)}
        log_to_json(result)

        if final_confidence > 80: # Lowered threshold slightly because Ensemble is stricter
            shutil.copy(mp3_path, os.path.join(OUTPUT_DIR, f"{best_word}_{mp3}"))
            print(f"✅ MATCH: {best_word} ({final_confidence}%) | Heard: {clean_guess}")
        else:
            print(f"❌ LOW: {clean_guess} -> {best_word} ({final_confidence}%)")

    except Exception as e:
        print(f"Error on {mp3}: {e}")
    
    # Periodic memory cleanup for long runs
    gc.collect()

print("Processing complete. Results saved to match_results.jsonl")
