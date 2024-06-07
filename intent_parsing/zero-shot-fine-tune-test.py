from transformers import BartForSequenceClassification, BartTokenizer
from pandas import read_csv
from pprint import pprint
from utils import get_best_available_device
from sklearn.metrics import classification_report, accuracy_score

import torch
import argparse


def single_query(classify_query):
    """Test the fine-tuned model on a single query."""
    
    # Test the model with a new query
    new_query = "Why do we push the block at state S3 \
        instead of moving it to the right at S4?"
    
    predicted_intent = classify_query(new_query)
    print(f"Query: {new_query}")
    print(f"Predicted intent: {predicted_intent}")


def entire_dataset(df, label_mapping, classify_query, save_path=None):
    """Test the fine-tuned model on a dataset."""

    queries = df['text'].tolist()
    true_labels = df['intent'].tolist()

    # Classify all queries
    predicted_labels = [classify_query(query) for query in queries]

    # Add the predicted intents to the DataFrame
    df['predicted_intent'] = predicted_labels

    # Generate the classification report
    print(classification_report(true_labels, predicted_labels, 
            target_names=[f"intent_{val}" for val in label_mapping.values()]))
    print(f"Accuracy: {accuracy_score(true_labels, predicted_labels):.2f}")

    # Save the DataFrame with predictions to a new CSV file
    if save_path:
        df.to_csv(save_path, index=False)


if __name__=="__main__":
    # Initialize parser
    parser = argparse.ArgumentParser()
    
    parser.add_argument("dataset_path")
    parser.add_argument("model_path")

    # Load the model and tokenizer
    dataset_path = parser.parse_args().dataset_path
    saved_dir = parser.parse_args().model_path

    print(f"Reading dataset from {dataset_path}")
    print(f"Reading model from {saved_dir}")

    device = get_best_available_device()
    print(f"---Using device: {device}")

    df = read_csv(dataset_path)

    # Encode the labels to numerical values
    label_mapping = {label: idx for idx, label in 
                     enumerate(df['intent'].unique())}
    pprint(label_mapping)

    base_model_name = "facebook/bart-large-mnli"
    model = BartForSequenceClassification.from_pretrained(
        base_model_name, num_labels=3)
    model.to(device)
    tokenizer = BartTokenizer.from_pretrained(base_model_name)

    # Function to classify new queries
    def classify_query(query):
        inputs = tokenizer(query, return_tensors="pt", padding=True, 
                        truncation=True, max_length=512)
        inputs.to(device)
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_id = torch.argmax(logits, dim=-1).item()
        predicted_label = list(label_mapping.keys())[predicted_class_id]
        return predicted_label

    print("\nPredicting a single query on the base model...")
    single_query(classify_query)
    
    print("\nPredicting labels for the base model...")
    entire_dataset(df, label_mapping, classify_query, None)

    # Load the fine-tuned model and tokenizer for inference
    model = BartForSequenceClassification.from_pretrained(saved_dir)
    model.to(device)  # Move the model to device
    tokenizer = BartTokenizer.from_pretrained(saved_dir)

    print("\nPredicting a single query on the fine-tuned model...")
    single_query(classify_query)
    
    print("\nPredicting labels for the fine-tuned model...")
    entire_dataset(df, label_mapping, classify_query, None)