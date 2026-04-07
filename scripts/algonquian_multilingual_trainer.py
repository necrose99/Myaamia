# algonquian_multilingual_trainer.py
from transformers import MarianMTModel, MarianTokenizer, Seq2SeqTrainingArguments, Seq2SeqTrainer
import torch
from datasets import DatasetDict

class AlgonquianMultilingualTrainer:
    def __init__(self, dataset_builder, model_name="arcee/ai-algic-base"):
        self.dataset_builder = dataset_builder
        self.model_name = model_name
        
        # Load model and tokenizer
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)
        
        # Add special tokens for all Algonquian languages
        algonquian_langs = [
            'mia', 'sauk', 'men', 'cre', 'csw', 'crj', 'atj', 'pot', 'oji',
            'otw', 'ciw', 'kic', 'sha', 'mic', 'abe', 'aaq', 'mal', 'moo',
            'mua', 'unm', 'bft', 'arp', 'ats', 'chy', 'en'
        ]
        
        special_tokens = {
            "additional_special_tokens": [f"<{lang}>" for lang in algonquian_langs]
        }
        self.tokenizer.add_special_tokens(special_tokens)
        self.model.resize_token_embeddings(len(self.tokenizer))
    
    def prepare_datasets(self):
        """Prepare datasets with language tags."""
        df = self.dataset_builder.build_unified_dataset()
        datasets = self.dataset_builder.create_datasets(df)
        
        def tokenize_with_tags(examples):
            tokenized = {}
            for i, (src, src_lang, tgt_lang) in enumerate(zip(
                examples['source'], 
                examples['source_lang'], 
                examples['target_lang']
            )):
                # Add language tags
                src = f"<{src_lang}>{src}"
                tgt = f"<{tgt_lang}>{tgt}"
                
                tokenized_i = self.tokenizer(
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
        
        tokenized_datasets = datasets.map(
            tokenize_with_tags,
            batched=True
        )
        
        return tokenized_datasets
    
    def train(self, output_dir="./algonquian-multilingual"):
        """Train the multilingual model."""
        tokenized_datasets = self.prepare_datasets()
        
        training_args = Seq2SeqTrainingArguments(
            output_dir=output_dir,
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
            hub_model_id="algonquian-multilingual",
        )
        
        trainer = Seq2SeqTrainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["validation"],
            tokenizer=self.tokenizer,
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
        
        print("🚀 Training Algonquian multilingual model...")
        trainer.train()
        
        # Save model
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        return trainer
