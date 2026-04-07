from datasets import DatasetDict
from transformers import MarianMTModel, MarianTokenizer, Seq2SeqTrainingArguments, Seq2SeqTrainer
import torch

# Prepare datasets
train_size = int(len(unified_df) * 0.8)
val_size = int(len(unified_df) * 0.1)
test_size = len(unified_df) - train_size - val_size

train_df = unified_df.iloc[:train_size]
val_df = unified_df.iloc[train_size:train_size+val_size]
test_df = unified_df.iloc[train_size+val_size:]

# Create Hugging Face datasets
datasets = DatasetDict({
    'train': Dataset.from_dict({
        'source': train_df['source'].tolist(),
        'target': train_df['target'].tolist(),
        'lang_pair': [f"{row['source_lang']}-{row['target_lang']}" for _, row in train_df.iterrows()]
    }),
    'validation': Dataset.from_dict({
        'source': val_df['source'].tolist(),
        'target': val_df['target'].tolist(),
        'lang_pair': [f"{row['source_lang']}-{row['target_lang']}" for _, row in val_df.iterrows()]
    }),
    'test': Dataset.from_dict({
        'source': test_df['source'].tolist(),
        'target': test_df['target'].tolist(),
        'lang_pair': [f"{row['source_lang']}-{row['target_lang']}" for _, row in test_df.iterrows()]
    })
})

# Load a model pre-trained on indigenous languages
model_name = "arcee/ai-algic-base"  # Or use Helsinki-NLP/opus-mt-mul-en

tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# Add special tokens for language identification
special_tokens = {
    "additional_special_tokens": [
        "<mia>", "<sauk>", "<en>", "<other>"
    ]
}
tokenizer.add_special_tokens(special_tokens)
model.resize_token_embeddings(len(tokenizer))

# Tokenize function with language tags
def tokenize_with_tags(examples):
    tokenized = {}
    for i, (src, lang_pair) in enumerate(zip(examples['source'], examples['lang_pair'])):
        src_lang, tgt_lang = lang_pair.split('-')
        
        # Add language tags
        if src_lang == 'mia':
            src = f"<mia>{src}"
        elif src_lang == 'sauk':
            src = f"<sauk>{src}"
        else:
            src = src
            
        if tgt_lang == 'mia':
            tgt = f"<mia>{tgt}"
        elif tgt_lang == 'sauk':
            tgt = f"<sauk>{tgt}"
        else:
            tgt = tgt
        
        tokenized_i = tokenizer(
            src,
            tgt,
            return_tensors="pt",
            padding=True,
            truncation=True
        )
        
        for k, v in tokenized_i.items():
            if k not in tokenized:
                tokenized[k] = []
            tokenized[k].append(v)
    
    for k in tokenized:
        tokenized[k] = torch.stack(tokenized[k])
    
    return tokenized

# Tokenize datasets
tokenized_datasets = datasets.map(
    tokenize_with_tags,
    batched=True
)

# Training arguments
training_args = Seq2SeqTrainingArguments(
    output_dir="./algic-multilingual",
    evaluation_strategy="epoch",
    learning_rate=5e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    predict_with_generate=True,
    fp16=torch.cuda.is_available(),
    num_train_epochs=30,
    save_steps=100,
    save_total_limit=2,
    push_to_hub=True,
    hub_model_id="algic-multilingual",
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
print("🚀 Training Algic multilingual model...")
trainer.train()

# Save model
model.save_pretrained("./algic-multilingual")
tokenizer.save_pretrained("./algic-multilingual")
