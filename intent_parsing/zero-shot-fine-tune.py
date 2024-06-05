import wandb

from os import environ
from pandas import read_csv
from numpy import argmax
from utils import get_best_available_device

from datasets import Dataset, DatasetDict
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from transformers import BartForSequenceClassification, BartTokenizer, Trainer, TrainingArguments


def main():
    # Step 1: Read the CSV file using Pandas
    df = read_csv('./data/combined_dataset.csv')

    # Convert labels to start from 0
    df['label'] = df['label'] - 1

    # Step 2: Convert the Pandas DataFrame to a Hugging Face Dataset
    dataset = Dataset.from_pandas(df)
    dataset = dataset.class_encode_column("label")

    # Step 3: Split the dataset into training and testing sets
    split = dataset.train_test_split(test_size=0.2, stratify_by_column="label", seed=13)
    dataset_dict = DatasetDict({
        'train': split['train'],
        'test': split['test']
    })

    # Step 4: Set up the tokenizer and model
    tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-mnli')
    model = BartForSequenceClassification.from_pretrained('facebook/bart-large-mnli', num_labels=3)

    # Tokenize the dataset
    def preprocess_function(examples):
        return tokenizer(examples['text'], padding='max_length', truncation=True)

    encoded_dataset = dataset_dict.map(preprocess_function, batched=True)

    # Set format for PyTorch
    encoded_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])

    device = get_best_available_device()
    model.to(device)  # Move the model to device
    print(f"Using device: {device}")

    # Step 5: Define training arguments
    training_args = TrainingArguments(
        output_dir='./results',
        report_to="wandb",
        eval_strategy='epoch',
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
    )

    # # Step 6: Define the compute_metrics function
    # def compute_metrics(p):
    #     pred, labels = p
    #     pred = argmax(pred, axis=1)
    #     precision, recall, f1, _ = precision_recall_fscore_support(labels, pred, average='weighted')
    #     acc = accuracy_score(labels, pred)
    #     return {'accuracy': acc, 'precision': precision, 'recall': recall, 'f1': f1}
    
    def compute_metrics(p):
        # Extract the logits and labels from the predictions
        logits, labels = p.predictions, p.label_ids
        
        # Ensure logits are in the correct shape (batch_size, num_labels)
        # If the logits are 3D (batch_size, sequence_length, num_labels)
        if logits.ndim == 3:
            # Take the first token's logits 
            # (usually [CLS] token for classification)
            logits = logits[:, 0, :]  

        # Calculate the predicted labels
        pred = argmax(logits, axis=1)
        
        # Calculate precision, recall, f1, and accuracy
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, pred, average='weighted')
        acc = accuracy_score(labels, pred)
        
        return {'accuracy': acc, 'precision': precision, 
                'recall': recall, 'f1': f1}


    # Step 7: Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=encoded_dataset['train'],
        eval_dataset=encoded_dataset['test'],
        compute_metrics=compute_metrics
    )

    # Step 8: Train the model
    trainer.train()


if __name__ == "__main__":
    # set the wandb project where this run will be logged
    environ["WANDB_PROJECT"] = "zero-shot-classification"

    # save your trained model checkpoint to wandb
    environ["WANDB_LOG_MODEL"] = "true"

    # turn off watch to log faster
    environ["WANDB_WATCH"] = "false"
    
    main()
