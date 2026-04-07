# !/usr/bin/env python3
"""
Train Sauk-English translation model.
"""
import torch
from transformers import MarianMTModel, MarianTokenizer, Seq2SeqTrainingArguments, Seq2SeqTrainer
from datasets import Dataset, DatasetDict
import pandas as pd
from pathlib import Path

# Load extracted data
print("Loading Sauk dictionary data...")
csv_path = "sauk_dictionary.csv"
if not Path(csv_path).exists():
    print("❌ First run: python extract_sauk.py sauk_dictionary.pdf")
    exit(1)

df = pd.read_csv(csv_path)
print(f"Loaded {len(df)} entries")

# Create parallel sentences (simple approach for demo)
# In reality, you'd want to pair each Sauk word with example sentences
def create_parallel_data(df):
    """Create simple word-translation pairs."""
    sources = []
    targets = []
    
    for _, row in df.iterrows():
        if pd.notna(row.get('headword')) and pd.notna(row.get('definition')):
            # Sauk word -> English definition
            sources.append(row['headword'])
            targets.append(row['definition'])
            
            # English definition -> Sauk word (reverse direction)
            sources.append(row['definition'])
            targets.append(row['headword'])
    
    return sources, targets

sources, targets = create_parallel_data(df)

# Create dataset
from datasets import DatasetDict
dataset = DatasetDict({
    'train': Dataset.from_dict({
        'source': sources[:int(len(sources)*0.8)],
        'target': targets[:int(len(sources)*0.8)]
    }),
    'validation': Dataset.from_dict({
        'source': sources[int(len(sources)*0.8):int(len(sources)*0.9)],
        'target': targets[int(len(sources)*0.8):int(len(sources)*0.9)]
    }),
    'test': Dataset.from_dict({
        'source': sources[int(len(sources)*0.9):],
        'target': targets[int(len(sources)*0.9):]
    })
})

# Load model and tokenizer
print("Loading MarianMT model...")
model_name = "Helsinki-NLP/opus-mt-mul-en"  # Good for indigenous languages
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# Tokenize function
def tokenize_function(examples):
    return tokenizer(
        examples['source'], 
        examples['target'],
        return_tensors="pt",
        padding="max_length",
        truncation=True
    )

# Tokenize datasets
print("Tokenizing datasets...")
tokenized_datasets = dataset.map(
    tokenize_function, 
    batched=True
)

# Training arguments
training_args = Seq2SeqTrainingArguments(
    output_dir="./sauk-translator",
    evaluation_strategy="epoch",
    learning_rate=5e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    predict_with_generate=True,
    fp16=torch.cuda.is_available(),
    num_train_epochs=30,
    save_steps=100,
    save_total_limit=2,
    logging_dir="./logs",
    logging_steps=10,
    report_to="none",
)

# Trainer
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
    tokenizer=tokenizer,
    data_collator=lambda data: {
        "input_ids": data["input_ids"].cuda() if torch.cuda.is_available() else data["input_ids"],
        "attention_mask": data["attention_mask"].cuda() if torch.cuda.is_available() else data["attention_mask"],
        "labels": data["labels"].cuda() if torch.cuda.is_available() else data["labels"],
    } if torch.cuda.is_available() else {
        "input_ids": data["input_ids"],
        "attention_mask": data["attention_mask"],
        "labels": data["labels"],
    }
)

# Train!
print("🚀 Starting training...")
trainer.train()

# Save model
model.save_pretrained("./sauk-translator")
tokenizer.save_pretrained("./sauk-translator")

print("✅ Training complete! Model saved to ./sauk-translator")
