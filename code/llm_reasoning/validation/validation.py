import argparse
import json
from pprint import pprint
from jsonschema import validate  # for validating JSON objects against a schema


# Steps to validate a Sokoban explanation:
# 1. Get the initial LLM response to the Sokoban question.
# 2. Prepare the conversion request by combining the prompt with the initial response.
# 3. Send this conversion request to an LLM.
# 4. Receive the JSON output from the LLM.
# 5. Use a JSON parser to ensure the output is valid JSON. If it's not, you might need to ask the LLM to correct it.
# 6. Feed the JSON output into the validation script.


def get_json_conversion_prompt(original_response):
    return f"""
    Please convert the following natural language response about a Sokoban problem into a JSON format adhering to this schema:
    
    ```json
    {{
      "questionType": "string (one of: planValidity, actionTaken, actionNotTaken, actionComparison)",
      "conclusion": "string (one of: valid, invalid, partially valid, inconclusive)",
      "reasoning": [
        {{
          "step": "integer",
          "explanation": "string",
          "relevantAction": "string (optional)",
          "preconditionsSatisfied": "boolean (optional)",
          "effectsConsistent": "boolean (optional)"
        }}
      ],
      "referencedGameElements": ["string"],
      "confidenceScore": "number (between 0 and 1)",
      "relevantActions": ["string"]
    }}
    ```
    
    Important notes:
    1. Determine the questionType based on the content of the response.
    2. Break down the reasoning into clear, numbered steps.
    3. Include relevantActions based on the questionType:
       - For planValidity: empty array
       - For actionTaken or actionNotTaken: array with one action
       - For actionComparison: array with two actions
    4. Extract referencedGameElements from the response.
    5. Estimate a confidenceScore based on the depth and clarity of the explanation.
    
    Here's the response to convert:
    
    {original_response}
    """


def get_schema():
    """
    # Return the JSON schema for Sokoban plan explanations
    # The schema defines the structure of the JSON object that represents a Sokoban plan explanation.
    # The schema also specifies the constraints that the JSON object should adhere to.
    # The constraints include the allowed values for certain fields and the relationships between different fields.
    # Note: There are 4 types of questions: planValidity, actionTaken, actionNotTaken, and actionComparison.
    """
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "questionType": {
                "type": "string",
                "enum": ["planValidity", "actionTaken", "actionNotTaken", "actionComparison"]
            },
            "conclusion": {
                "type": "string",
                "enum": ["valid", "invalid", "partially valid", "inconclusive"]
            },
            "reasoning": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "step": {"type": "integer"},
                        "explanation": {"type": "string"},
                        "relevantAction": {"type": "string"},
                        "preconditionsSatisfied": {"type": "boolean"},
                        "effectsConsistent": {"type": "boolean"}
                    },
                    "required": ["step", "explanation"]
                }
            },
            "referencedGameElements": {
                "type": "array",
                "items": {"type": "string"}
            },
            "confidenceScore": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
            },
            "relevantActions": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["questionType", "conclusion", "reasoning", "relevantActions"]
    }


def validate_plan_validity(explanation, plan):
    if plan is None:
        raise ValueError("Plan must be provided for planValidity questions")

    invalid_steps = [step for step in explanation['reasoning'] if not step.get('preconditionsSatisfied')]
    if invalid_steps and explanation['conclusion'] != 'invalid':
        raise ValueError("Conclusion should be 'invalid' if any steps have unsatisfied preconditions")

    mentioned_steps = [step['relevantAction'] for step in explanation['reasoning'] if 'relevantAction' in step]
    if not all(action in plan for action in mentioned_steps):
        raise ValueError("All mentioned steps should be in the provided plan")

    explained_invalid_steps = set(step['relevantAction'] for step in invalid_steps if 'relevantAction' in step)
    if len(explained_invalid_steps) < len(invalid_steps):
        raise ValueError("All invalid steps should have a unique explanation")

    plan_elements = set()
    for action in plan:
        plan_elements.update(action.split())
    if not set(explanation['referencedGameElements']).issubset(plan_elements):
        raise ValueError("All referenced game elements should appear in the plan")


def validate_action_taken(explanation, question_info):
    if len(explanation['relevantActions']) != 1:
        raise ValueError("actionTaken questions should have exactly one relevant action")

    if explanation['relevantActions'] != question_info['action']:
        raise ValueError("Relevant action doesn't match the provided question info")

    if explanation['conclusion'] not in ['valid', 'invalid']:
        raise ValueError("Conclusion for actionTaken should be either 'valid' or 'invalid'")

    precondition_steps = [step for step in explanation['reasoning'] if 'preconditionsSatisfied' in step]
    if not precondition_steps:
        raise ValueError("At least one step should mention preconditions for actionTaken")


def validate_action_not_taken(explanation, question_info):
    if len(explanation['relevantActions']) != 1:
        raise ValueError("actionNotTaken questions should have exactly one relevant action")

    if explanation['relevantActions'] != question_info['action']:
        raise ValueError("Relevant action doesn't match the provided question info")

    if explanation['conclusion'] not in ['valid', 'invalid']:
        raise ValueError("Conclusion for actionNotTaken should be either 'valid' or 'invalid'")

    precondition_steps = [step for step in explanation['reasoning'] if 'preconditionsSatisfied' in step]
    if not precondition_steps:
        raise ValueError("At least one step should mention preconditions for actionNotTaken")


def validate_action_comparison(explanation, question_info):
    if len(explanation['relevantActions']) != 2:
        raise ValueError("actionComparison questions should have exactly two relevant actions")

    if set(explanation['relevantActions']) != set(question_info['actions']):
        raise ValueError("Relevant actions don't match the provided question info")

    if explanation['conclusion'] not in ['valid', 'invalid', 'partially valid']:
        raise ValueError("Conclusion for actionComparison should be 'valid', 'invalid', or 'partially valid'")

    precondition_steps = [step for step in explanation['reasoning'] if 'preconditionsSatisfied' in step]
    effect_steps = [step for step in explanation['reasoning'] if 'effectsConsistent' in step]
    if not precondition_steps or not effect_steps:
        raise ValueError("Reasoning should mention both preconditions and effects for actionComparison")


def validate_sokoban_explanation(explanation: dict, initial_state: set, question_info: dict, plan: list):
    """
    Validate an explanation for a Sokoban plan against the JSON schema and additional constraints.
    @param explanation: The explanation to validate. Should be a dictionary representing a Sokoban plan explanation.
    @param initial_state: The initial state of the Sokoban plan. Should be a set of strings representing game elements.
        Note that the initial state consists of the objects and their initial positions.
    @param question_info: Information about the question that was asked.
        Should be a dictionary with keys 'type', 'action', and/or 'actions'.
    @param plan: The Sokoban plan. Should be a list of strings representing the actions in the plan.
    """
    # Validate against JSON schema
    # Raises an exception if the explanation does not adhere to the schema
    validate(instance=explanation, schema=get_schema())

    # Check question type
    assert explanation['questionType'] in ['planValidity', 'actionTaken', 'actionNotTaken', 'actionComparison'], \
        "Invalid question type"
    assert explanation['questionType'] == question_info['type'], \
        "Question type doesn't match the provided question info"

    # Check conclusion
    assert explanation['conclusion'] in ['valid', 'invalid', 'partially valid', 'inconclusive'], "Invalid conclusion"

    # Check reasoning steps
    assert len(explanation['reasoning']) > 0, "Reasoning should have at least one step"

    # Check referenced game elements
    game_elements = set(explanation['referencedGameElements'])
    assert all(element in initial_state for element in game_elements), \
        "All referenced game elements should be in the initial state"

    # Check actions based on question type
    if explanation['questionType'] == 'planValidity':
        assert len(explanation['relevantActions']) == 0, "Plan validity questions should not have relevant actions"

    elif explanation['questionType'] in ['actionTaken', 'actionNotTaken']:
        assert len(explanation['relevantActions']) == 1, \
            f"{explanation['questionType']} questions should have exactly one relevant action"
        assert explanation['relevantActions'] == question_info['action'], \
            "Relevant action doesn't match the provided question info"

    elif explanation['questionType'] == 'actionComparison':
        assert len(explanation['relevantActions']) == 2, \
            "Action comparison questions should have exactly two relevant actions"
        assert set(explanation['relevantActions']) == set(question_info['actions']), \
            "Relevant actions don't match the provided question info"

    # Check if relevant actions are mentioned in reasoning
    for action in explanation['relevantActions']:
        assert any(step.get('relevantAction') == action for step in explanation['reasoning']), \
            f"Action {action} should be mentioned in reasoning"

    # Check preconditions and effects (if applicable)
    if explanation['questionType'] != 'planValidity':
        precondition_steps = [step for step in explanation['reasoning'] if 'preconditionsSatisfied' in step]
        assert len(precondition_steps) > 0, "At least one step should mention preconditions"
        assert all(step['preconditionsSatisfied'] for step in precondition_steps), \
            "All mentioned preconditions should be satisfied"

        effect_steps = [step for step in explanation['reasoning'] if 'effectsConsistent' in step]
        assert len(effect_steps) > 0, "At least one step should mention effects"
        assert all(step['effectsConsistent'] for step in effect_steps), "All mentioned effects should be consistent"

    # Check confidence score
    assert 0 <= explanation['confidenceScore'] <= 1, "Confidence score should be between 0 and 1"

    # Specific checks based on question type
    if explanation['questionType'] == 'planValidity':
        validate_plan_validity(explanation, plan)
    elif explanation['questionType'] == 'actionTaken':
        validate_action_taken(explanation, question_info)
    elif explanation['questionType'] == 'actionNotTaken':
        validate_action_not_taken(explanation, question_info)
    elif explanation['questionType'] == 'actionComparison':
        validate_action_comparison(explanation, question_info)


def process_sokoban_response(initial_state):
    """
    Process a Sokoban explanation response from LLM.
    @param initial_state: The initial state of the Sokoban plan.
    @return: The processed Sokoban explanation response.
    """
    # # Step 1: Prepare conversion request
    # conversion_prompt = get_json_conversion_prompt(original_response)

    # # Step 2: Get JSON conversion from LLM
    # json_response = get_llm_validation_response(conversion_prompt)  # Placeholder for JSON response

    # Until the `get_llm_response` function is implemented, we'll use the JSON response by
    # reading the file given by the command line argument `json_response_file`.
    with open(args.json_response_file, 'r') as f:
        json_response = f.read()

    # Step 3: Parse JSON (and handle potential errors)
    json_true: bool = False  # Flag to indicate successful JSON parsing
    parsed_response = None  # Placeholder for parsed JSON response
    while not json_true:
        try:
            parsed_response = json.loads(json_response)
            json_true = True  # JSON parsing successful

        except json.JSONDecodeError:  # Handle invalid JSON. Try one more time.
            # print("LLM produced invalid JSON. Requesting correction...")
            # correction_prompt = f"The previous response was not valid JSON. Please correct it:\n\n{json_response}"
            # json_response = get_llm_response(correction_prompt)

            # Until the `get_llm_response` function is implemented, we will exit
            exit("Invalid JSON response from LLM. Please correct the response and try again.")

    # Build the `question_info` dictionary from the command line arguments
    question_info = {
        "type": args.question_type,
    }
    if args.relevant_actions:
        question_info["action"] = args.relevant_actions

    # Step 4: Validate the response
    plan = [
        "moveup sokoban l19 l12",
        "moveleft sokoban l12 l11",
        "moveleft sokoban l11 l10",
        "pushdown sokoban l10 l17 l24 crate1",
        "pushdown sokoban l17 l24 l31 crate1",
        "moveleft sokoban l24 l23",
        "movedown sokoban l23 l30",
        "movedown sokoban l30 l37",
        "moveright sokoban l37 l38",
        "moveright sokoban l38 l39",
        "moveup sokoban l39 l32",
        "pushleft sokoban l32 l31 l30 crate1",
        "moveup sokoban l31 l24",
        "moveup sokoban l24 l17",
        "moveup sokoban l17 l10",
        "movedown sokoban l12 l19",
        "pushleft sokoban l19 l18 l17 crate2",
        "moveup sokoban l18 l11",
        "moveleft sokoban l11 l10",
        "pushdown sokoban l10 l17 l24 crate2",
        "pushdown sokoban l17 l24 l31 crate2",
        "pushdown sokoban l24 l31 l38 crate2",
        "moveup sokoban l31 l24",
        "moveleft sokoban l24 l23",
        "moveleft sokoban l23 l22",
        "movedown sokoban l22 l29",
        "movedown sokoban l29 l36",
        "moveright sokoban l36 l37",
        "pushright sokoban l37 l38 l39 crate2",
        "moveup sokoban l38 l31",
        "moveup sokoban l31 l24",
        "moveleft sokoban l24 l23",
        "pushdown sokoban l23 l30 l37 crate1"
    ]
    try:
        validate_sokoban_explanation(parsed_response, initial_state, question_info, plan)
        print("Validation successful!")
    except ValueError as e:
        print(f"Validation failed: {str(e)}")

    return parsed_response


def main():
    # The `initial_state` consists of the objects and the initial states
    initial_state = {
        "sokoban", "crate1", "crate2", "l1", "l10", "l11", "l12", "l17", "l18", "l19", "l22",
        "l23", "l24", "l29", "l30", "l31", "l32", "l33", "l36", "l37", "l38", "l39", "l40"}
    initial_state.update(
        {"crate crate1", "crate crate2", "leftOf l10 l11", "leftOf l11 l12", "leftOf l17 l18",
         "leftOf l18 l19", "leftOf l22 l23", "leftOf l23 l24", "leftOf l29 l30", "leftOf l30 l31",
         "leftOf l31 l32", "leftOf l32 l33", "leftOf l36 l37", "leftOf l37 l38", "leftOf l38 l39",
         "leftOf l39 l40", "below l17 l10", "below l18 l11", "below l19 l12", "below l24 l17",
         "below l29 l22", "below l30 l23", "below l31 l24", "below l36 l29", "below l37 l30",
         "below l38 l31", "below l39 l32", "below l40 l33", "at sokoban l19", "at crate1 l17",
         "at crate2 l18", "clear l1", "clear l10", "clear l11", "clear l12", "clear l22",
         "clear l23", "clear l24", "clear l29", "clear l30", "clear l31", "clear l32",
         "clear l33", "clear l36", "clear l37", "clear l38", "clear l39", "clear l40"}
    )

    processed_response = process_sokoban_response(initial_state)
    # print("Processed response:")
    # print(json.dumps(processed_response, indent=2))


if __name__ == "__main__":
    argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Validate Sokoban explanations')

    parser.add_argument('json_response_file', type=str, help='The JSON response file.')
    parser.add_argument('question_type', type=str, help='The type of question. Should be one of planValidity, actionTaken, actionNotTaken, or actionComparison.')
    parser.add_argument('--relevant_actions', type=str, nargs="*", help='The relevant actions for the question. Seperate multiple actions with spaces.')

    args = parser.parse_args()

    main()
