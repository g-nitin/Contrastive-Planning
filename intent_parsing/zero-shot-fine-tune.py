import wandb

from os import environ, listdir, path, system
from pandas import read_csv
from numpy import argmax
from utils import get_best_available_device
from datetime import datetime

from datasets import Dataset, DatasetDict
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from transformers import BartForSequenceClassification, BartTokenizer, Trainer, TrainingArguments


def main():
    # Step 1: Read the CSV file using Pandas
    df = read_csv('data/sokoban_final_dataset.csv')

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
    print(f"---Using device: {device}")

    # Step 5: Define training arguments
    out_dir = "./fine-tune_results"
    training_args = TrainingArguments(
        report_to="wandb",
        output_dir=out_dir,
        eval_strategy='steps',
        eval_steps=1000,                # Evaluate every 1000 steps
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=8,  # Accumulate gradients over 4 steps
        num_train_epochs=3,
        weight_decay=0.01,
        fp16=True,                      # Enable mixed precision training
        logging_steps=500,              # Log less frequently
        save_total_limit=1,             # Limit the total number of checkpoints
        save_steps=1000,                # Save checkpoint every 1000 steps
    )

    def compute_metrics(p):
        # Extract the logits and labels from the predictions
        logits, labels = p.predictions, p.label_ids

        # If logits is a tuple, extract the first element
        if isinstance(logits, tuple):
            logits = logits[0]
        
        # Ensure logits are in the correct shape (batch_size, num_labels)
        if logits.ndim == 3:  # If the logits are 3D (batch_size, sequence_length, num_labels)
            logits = logits[:, 0, :]  # Take the first token's logits (usually [CLS] token for classification)

        # Calculate the predicted labels
        pred = argmax(logits, axis=1)
        
        # Calculate precision, recall, f1, and accuracy
        precision, recall, f1, _ = precision_recall_fscore_support(labels, pred, average='weighted')
        acc = accuracy_score(labels, pred)
        return {'accuracy': acc, 'precision': precision, 'recall': recall, 'f1': f1}


    # Step 7: Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=encoded_dataset['train'],
        eval_dataset=encoded_dataset['test'],
        compute_metrics=compute_metrics
    )

    # Step 8: Monitor Disk Space and Add Debug Prints
    def clear_checkpoints():
        checkpoints = [f for f in listdir(out_dir) if 'checkpoint' in f]
        for checkpoint in checkpoints:
            path = path.join('./results', checkpoint)
            if path.isdir(path):
                print(f"Deleting checkpoint: {path}")
                system(f"rm -rf {path}")

    # Function to monitor disk space (debugging purpose)
    def monitor_disk_space():
        import shutil
        total, used, free = shutil.disk_usage("./")
        print(f"Disk usage: {used / (2**30):.2f} GB used, {free / (2**30):.2f} GB free")

    # Step 9: Train the model with intermediate cleanup and verbose output
    try:
        for epoch in range(training_args.num_train_epochs):
            print(f"Epoch {epoch+1}/{training_args.num_train_epochs}")
            trainer.train()
            clear_checkpoints()
            monitor_disk_space()
        print("--Training finished.")
    except Exception as e:
        print(f"Error during training: {e}")

    # Step 10: Evaluate the model
    try:
        eval_result = trainer.evaluate()
        print(eval_result)
        print("--Evaluation finished.")
    except Exception as e:
        print(f"Error during evaluation: {e}")

    # Step 11: Save the model and tokenizer 
    # with date and time in the directory name
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_directory = f'saved_models/saved_model_{current_time}'
    try:
        model.save_pretrained(save_directory)
        tokenizer.save_pretrained(save_directory)
        print(f"--Model saved at {save_directory}")
    except Exception as e:
        print(f"Error during model saving: {e}")


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
