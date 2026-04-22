import json

# Load your clean dictionary into memory
dictionary = {}
with open('training_data.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        # Store Myaamia -> English mapping
        dictionary[data['input']] = data['output']

def get_smart_phoneme(word):
    # 1. Check if we already know this word exactly
    if word in dictionary:
        print(f"🎯 Exact match found for {word}")
        # Use the dictionary to help the LLM generate the IPA
        return call_llama_with_context(word, dictionary[word])
    else:
        # 2. If it's a new word, let the LLM hypothesize
        return call_llama_hypothesize(word)