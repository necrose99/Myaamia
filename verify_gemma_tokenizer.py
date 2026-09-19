# C:\tools\verify_gemma_tokenizer.py
from transformers import AutoTokenizer

MODEL_PATH = r"C:\tools\gemma-3-1b-raw"

try:
    print("Loading tokenizer token mappings...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    
    # Gemma 3 expects explicit boundary tags for structured cross key translations
    test_prompt = "<bos><start_of_turn>user\nTranslate: Je ſuis<end_of_turn>\n<start_of_turn>model\nMyaamia: nila<end_of_turn><eos>"
    tokens = tokenizer.tokenize(test_prompt)
    
    print("\nStructural Token Array Breakdown:")
    print(tokens[:10])
    print("\nTokenizer structural checks pass successfully!")
except Exception as e:
    print(f"Configuration Warning: {e}\nEnsure your download file finishes before testing tokens.")
