import argparse
import wandb

from os import environ
from utils import get_best_available_device
from datetime import datetime

from pandas import read_csv
from numpy import argmax
from datasets import Dataset, DatasetDict
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, classification_report)
from transformers import (
    BartForSequenceClassification, BartTokenizer, Trainer, TrainingArguments)

"""
This script demonstrates how to fine-tune a pre-trained model on a dataset.
"""


def ensure_logit_shape(logits):
    # If logits is a tuple, extract the first element
    if isinstance(logits, tuple):
        logits = logits[0]
    
    # Ensure logits are in the correct shape (batch_size, num_labels)
    # If the logits are 3D (batch_size, sequence_length, num_labels)
    if logits.ndim == 3:
        # Take the first token's logits 
        # (usually [CLS] token for classification)
        logits = logits[:, 0, :]  

    return logits


def main():
    # Initialize parser
    parser = argparse.ArgumentParser()

    parser.add_argument("dataset_path")

    # Load the model and tokenizer
    dataset_path = parser.parse_args().dataset_path
    print(f"Reading dataset from {dataset_path}")

    # Step 1: Read the CSV file using Pandas
    df = read_csv(dataset_path)

    # Encode the labels to numerical values
    label_mapping = {label: idx for idx, label in \
                     enumerate(df['intent'].unique())}
    df['label'] = df['intent'].map(label_mapping)

    # Step 2: Convert the Pandas DataFrame to a Hugging Face Dataset
    dataset = Dataset.from_pandas(df)
    dataset = dataset.class_encode_column("label")

    # Step 3: Split the dataset into training and testing sets
    split = dataset.train_test_split(test_size=0.2,

                                     stratify_by_column="label", seed=13)
    dataset_dict = DatasetDict({
        'train': split['train'],
        'test': split['test']
    })

    # Step 4: Set up the tokenizer and model
    tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-mnli')
    model = BartForSequenceClassification.from_pretrained(
        'facebook/bart-large-mnli', num_labels=3)

    # Tokenize the dataset
    def preprocess_function(examples):
        return tokenizer(examples['text'], 
                         padding='max_length', 
                         truncation=True)

    encoded_dataset = dataset_dict.map(preprocess_function, batched=True)

    # Set format for PyTorch
    encoded_dataset.set_format(
        type='torch', columns=['input_ids', 'attention_mask', 'label'])

    device = get_best_available_device()
    model.to(device)  # Move the model to device
    print(f"\nUsing device: {device}\n")

    # Step 5: Define training arguments
    out_dir = "./fine-tune_results"
    training_args = TrainingArguments(
        report_to="wandb",
        output_dir=out_dir,
        eval_strategy='steps',
        eval_steps=1000,                # Evaluate every 1000 steps
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        gradient_accumulation_steps=1,  # Accumulate gradients over `n` steps
        num_train_epochs=3,
        weight_decay=0.01,
        fp16=True,                      # Enable mixed precision training
        logging_steps=100,              # Log frequency
        save_total_limit=2,             # Limit the total number of checkpoints
        save_steps=500,                 # Save checkpoint every `n` steps
    )

    def compute_metrics(p):
        # Extract the logits and labels from the predictions
        logits, labels = p.predictions, p.label_ids

        logits = ensure_logit_shape(logits)

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
    print(f"\nTraining Complete")

    # Step 9: Evaluate the model
    eval_result = trainer.evaluate()
    print(eval_result)
    print(f"\nEvaluation Complete")

    # Make predictions on the test dataset
    preds_output = trainer.predict(encoded_dataset['test'])
    logits = preds_output.predictions

    logits = ensure_logit_shape(logits)

    predictions = argmax(logits, axis=1)
    labels = preds_output.label_ids

    # Generate and print the classification report
    report = classification_report(labels, predictions, 
                                   target_names=['intent 1', 'intent 2', 'intent 3'])
    print("\nClassification Report for Fine-tuned Model on Evaluation Set:")
    print(report)

    # Calculate and print accuracy for the fine-tuned model
    fine_tuned_accuracy = accuracy_score(labels, predictions)
    print(f"Accuracy for Fine-tuned Model: {fine_tuned_accuracy:.2f}")

    # Step 10: Save the model and tokenizer 
    # with date and time in the directory name
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_directory = f'saved_models/saved_model_{current_time}'
    model.save_pretrained(save_directory)
    tokenizer.save_pretrained(save_directory)
    print(f"\nModel saved at {save_directory}")


if __name__ == "__main__":
    # set the wandb project where this run will be logged
    environ["WANDB_PROJECT"] = "zero-shot-classification"

    # save your trained model checkpoint to wandb
    environ["WANDB_LOG_MODEL"] = "true"

    # turn off watch to log faster
    environ["WANDB_WATCH"] = "false"

    tempDir = "/local/niting/"
    environ['TRANSFORMERS_CACHE'] = tempDir
    environ['HF_DATASETS_CACHE'] = tempDir
    environ['HF_HOME'] = tempDir
    
    main()
