from transformers import BartForSequenceClassification, BartTokenizer, pipeline
from utils import get_best_available_device
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score
import argparse

# Initialize parser
parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("model_path")

# Load the model and tokenizer
saved_dir = parser.parse_args().model_path  # Read arguments from Command Line
print(f"Reading model from {saved_dir}")

model = BartForSequenceClassification.from_pretrained(saved_dir)
tokenizer = BartTokenizer.from_pretrained(saved_dir)

device = get_best_available_device()
model.to(device)  # Move the model to device
print(f"---Using device: {device}")

# Load the CSV file into a DataFrame
df = pd.read_csv('data/sokoban_final_dataset.csv')
print(f"Number of rows in the dataset: {df.shape[0]}\n")

# Define the candidate labels and their corresponding intent numbers
candidate_labels = ["Why is action A not used in the plan?", 
                    "Why is action A used in the plan?", 
                    "Why is action A used rather than action B?"]

intent_to_label = {label: intent for label, intent in zip(
    candidate_labels, range(1, 4))}

# Load a pre-trained zero-shot classification pipeline
classifier = pipeline("zero-shot-classification", 
                      model=model, tokenizer=tokenizer)

# Function to get predictions for each text
def get_prediction(text):
    result = classifier(text, candidate_labels)
    predicted_label = intent_to_label[result['labels'][0]]
    return predicted_label

# Apply the function to the text column
df['predicted_label'] = df['text'].apply(get_prediction)

# Compare predicted labels with actual labels
y_true = df['label']
y_pred = df['predicted_label']

# Print the classification report
print(classification_report(y_true, y_pred))
print(f"Accuracy: {accuracy_score(y_true, y_pred):.2f}")