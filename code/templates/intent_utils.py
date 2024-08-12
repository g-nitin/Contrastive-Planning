from transformers import BartForSequenceClassification, BartTokenizer
import torch
from torch_utils import get_best_available_device


def get_intent(query: str) -> tuple[str, int]:
    """
    Returns the intent of the query based on the fine-tuned zero-shot classification model.
    :param query: The query to classify.
    :return: A two-tuple containing the predicted intent and its corresponding label.
    The mapping is as follows:
        'Why is action A not used in the plan?': 1,
        'Why is action A used in the plan?': 2,
        'Why is action A used rather than action B?': 3,
    """
    device = get_best_available_device()
    # print(f"---Using device: {device}")

    # Load the fine-tuned model
    saved_dir = "../../models/grounded_saved_model_20240606_230822"
    model = BartForSequenceClassification.from_pretrained(saved_dir)
    model.to(device)  # Move the model to device
    tokenizer = BartTokenizer.from_pretrained(saved_dir)

    label_mapping = {
        'Why is action A not used in the plan?': 1,
        'Why is action A used in the plan?': 2,
        'Why is action A used rather than action B?': 3,
    }

    def classify_query(query):
        inputs = tokenizer(query, return_tensors="pt", padding=True,
                           truncation=True, max_length=512)
        inputs.to(device)
        outputs = model(**inputs)
        predicted_class_id = torch.argmax(outputs.logits, dim=-1).item()
        predicted_label = list(label_mapping.keys())[predicted_class_id]
        return predicted_label

    # query = "Why do we push the block at state S3 instead of moving it to the right at S4?"
    predicted_intent = classify_query(query)
    # print(f"Query: {query}")
    # print(f"Predicted intent: {predicted_intent}")
    return predicted_intent, label_mapping[predicted_intent]


if __name__ == "__main__":
    query = "Why is moveLeft sokoban x1 y1 not used in the plan?"
    print(f"Query: {query}")
    print(f"Predicted intent: {get_intent(query)}")
