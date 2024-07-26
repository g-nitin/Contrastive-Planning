from prompt import *

# prompt_action: dict[str, str] = {
#     "Prompt 2": "this is prompt 2",
#     "Prompt 3": "this is prompt 3",
#     "Prompt 4a": "this is prompt 4a",
#     "Prompt 4b": "this is prompt 4b",
#     "Prompt 4c-1": "this is prompt 4c-1",
#     "Prompt 4c-2": "this is prompt 4c-2",
#     "Prompt 5": "this is prompt 5"
# }
#
# p = Prompt("this is the problem", "this is the solution", prompt_action, True)
# print(p.prompt_4c())

# print(prompt_1(True).prompt_4c())

import json
from jsonschema import validate, ValidationError

# Define a JSON schema for validation
schema = {
    "type": "object",
    "properties": {
        "prompts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "problem": {"type": "string"},
                    "solution": {"type": "string"},
                    "prompt_actions": {"type": "object"}
                },
                "required": ["problem", "solution", "prompt_actions"]
            }
        }
    },
    "required": ["prompts"]
}

def load_and_validate_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Validate JSON data against the schema
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise ValueError(f"JSON validation error: {e.message}")

    return data

def parse_prompts(data):
    prompts = data['prompts']
    for idx, prompt in enumerate(prompts):
        problem = prompt['problem']
        solution = prompt['solution']
        prompt_actions = prompt['prompt_actions']

        print(f"Prompt {idx + 1}:")
        print("Problem:", problem)
        print("Solution:", solution)
        print("Prompt Actions:", prompt_actions)
        print("-" * 40)

# Example usage
try:
    json_data = load_and_validate_json('./prompts.json')
    parse_prompts(json_data)
except ValueError as e:
    print("Error:", e)
