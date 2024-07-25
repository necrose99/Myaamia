#!/usr/bin/python3
import json
from ollama import Client

client = Client()

def load_miami_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def query_ai_model(text):
    response = client.chat(model='tinyllama', messages=[
        {
            'role': 'system',
            'content': 'You are a Miami language assistant. Respond in Miami if possible, or English otherwise.',
        },
        {
            'role': 'user',
            'content': text,
        },
    ])
    return response['message']['content']

# Load Miami data
miami_data = load_miami_data("miami_dataset.json")

# Fine-tune the model (this is conceptual, actual implementation would vary)
# client.create(model='tinyllama', name='miami-llm', data=miami_data)

# Example usage
result = query_ai_model("How do you say 'hello' in Miami?")
print(result)