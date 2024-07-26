from rdflib import Graph
import os
import sys
import json
from jsonschema import validate, ValidationError

# Need to add the parent directory to the sys path to import the rdf_utils module
# More info: https://sentry.io/answers/import-files-from-a-different-folder-in-python/
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
import templates.rdf_utils as rdf_utils


def _prompt_basic(problem: str, solution: str, question: str, domain: str) -> str:
    """
    Helper function to generate a basic prompt.
    @param problem: The Sokoban problem in PDDL format.
    @param solution: The generated solution plan.
    @param question: The question to be answered.
    @param domain: The domain of the problem.
    @return: A formatted prompt string.
    """

    return f"""
    I have a {domain} problem with the following initial and goal states expressed in PDDL:

    **Initial and Goal States:**
    ```
    {problem}
    ```

    **Generated Solution Plan:**
    ```
    {solution}
    ```

    I need you to answer the following question in under 100 words by reasoning through the provided information:

    **Question:**
    ```
    {question}
    ```

    Hints:
        There are 8 actions for the Sokoban domain.
        The actions with the format of `move* ?x ?y` are the action that move the Sokoban from location `?x` to `?y`.
        The actions with the format of `push* ?x ?y ?z ?crate` are the action that push the Sokoban from `?x` to `?y` and `?crate` from location `?y` to `?z`.
    """


def _prompt_1_template(problem: str, solution: str, domain: str, include_ontology: bool) -> str:
    """
    Helper function to generate a prompt for the first question.
    @param problem: The Sokoban problem in PDDL format.
    @param solution: The generated solution plan.
    @param domain: The domain of the problem.
    @param include_ontology: Whether to include the ontology in the prompt.
    @return: A formatted prompt string.
    """
    to_return = _prompt_basic(problem, solution, "Is the plan, provided above, valid?", domain)

    if include_ontology:
        to_return += f"""
    For context, here is additional information about the actions for the domain. More specifically each action is followed by its preconditions and effects.

    **Action: (Precondition, Effect)**
    ```
    {{'movedown': (['sokoban ?sokoban', 'at ?sokoban ?x', 'below ?y ?x', 'clear ?y'],
                  ['at ?sokoban ?y', 'clear ?x', 'not (at ?sokoban ?x)', 'not (clear ?y)']),
     'moveleft': (['sokoban ?sokoban', 'at ?sokoban ?x', 'leftOf ?y ?x', 'clear ?y'],
                  ['at ?sokoban ?y', 'clear ?x', 'not (at ?sokoban ?x)', 'not (clear ?y)']),
     'moveright': (['sokoban ?sokoban', 'at ?sokoban ?x', 'leftOf ?x ?y', 'clear ?y'],
                   ['at ?sokoban ?y', 'clear ?x', 'not (at ?sokoban ?x)', 'not (clear ?y)']),
     'moveup': (['sokoban ?sokoban', 'at ?sokoban ?x', 'below ?x ?y', 'clear ?y'],
                ['at ?sokoban ?y', 'clear ?x', 'not (at ?sokoban ?x)', 'not (clear ?y)']),
     'pushdown': (['sokoban ?sokoban', 'crate ?crate', 'below ?y ?x', 'below ?z ?y', 'at ?sokoban ?x', 'at ?crate ?y', 'clear ?z'],
                  ['at ?sokoban ?y', 'at ?crate ?z', 'clear ?x', 'not (at ?sokoban ?x)', 'not (at ?crate ?y)', 'not (clear ?y)', 'not (clear ?z)']),
     'pushleft': (['sokoban ?sokoban', 'crate ?crate', 'leftOf ?y ?x', 'leftOf ?z ?y', 'at ?sokoban ?x', 'at ?crate ?y', 'clear ?z'],
                  ['at ?sokoban ?y', 'at ?crate ?z', 'clear ?x', 'not (at ?sokoban ?x)', 'not (at ?crate ?y)', 'not (clear ?z)', 'not (clear ?y)']),
     'pushright': (['sokoban ?sokoban', 'crate ?crate', 'leftOf ?x ?y', 'leftOf ?y ?z', 'at ?sokoban ?x', 'at ?crate ?y', 'clear ?z'],
                   ['at ?sokoban ?y', 'at ?crate ?z', 'clear ?x', 'not (at ?sokoban ?x)', 'not (at ?crate ?y)', 'not (clear ?z)', 'not (clear ?y)']),
     'pushup': (['sokoban ?sokoban', 'crate ?crate', 'below ?x ?y', 'below ?y ?z', 'at ?sokoban ?x', 'at ?crate ?y', 'clear ?z'],
                ['at ?sokoban ?y', 'at ?crate ?z', 'clear ?x', 'not (at ?sokoban ?x)', 'not (at ?crate ?y)', 'not (clear ?y)', 'not (clear ?z)'])}}
    ```
    """

    return to_return


def _single_ques_template(problem: str, solution: str, question: str, domain: str, action: str,
                          preconditions_action: list[str], effects_action: list[str],
                          include_ontology: bool) -> str:
    """
    Helper function to generate a prompt for a single question.
    @param problem: The Sokoban problem in PDDL format.
    @param solution: The generated solution plan.
    @param question: The question to be answered.
    @param domain: The domain of the problem.
    @param action: The specific action mentioned in the question.
    @param preconditions_action: The preconditions of the action.
    @param effects_action: The effects of the action.
    @param include_ontology: Whether to include the ontology in the prompt.
    @return: A formatted prompt string.
    """

    to_return = _prompt_basic(problem, solution, question, domain)

    if include_ontology:
        to_return += f"""
    For context, here is additional information about the specific action mentioned in the question:

    **Action:**
    ```
    {action}
    ```

    **Preconditions of the Action:**
    ```
    {preconditions_action}
    ```

    **Effects of the Action:**
    ```
    {effects_action}
    ```

    Using this information, please provide a short, logical response that addresses the question.
    """

    return to_return


def _double_ques_template(problem: str, solution: str, question: str, domain: str,
                          action_1: str, preconditions_1: list[str], effects_1: list[str],
                          action_2: str, preconditions_2: list[str], effects_2: list[str],
                          include_ontology: bool) -> str:
    """
    Helper function to generate a prompt for a question with two actions.
    @param problem: The Sokoban problem in PDDL format.
    @param solution: The generated solution plan.
    @param question: The question to be answered.
    @param domain: The domain of the problem.
    @param action_1: The first specific action mentioned in the question.
    @param preconditions_1: The preconditions of the first action.
    @param effects_1: The effects of the first action.
    @param action_2: The second specific action mentioned in the question.
    @param preconditions_2: The preconditions of the second action.
    @param effects_2: The effects of the second action.
    @param include_ontology: Whether to include the ontology in the prompt.
    @return: A formatted prompt string.
    """

    to_return = _prompt_basic(problem, solution, question, domain)

    if include_ontology:
        to_return += f"""
    For context, here is additional information about the specific actions mentioned in the question:

    **Action 1:**
    ```
    {action_1}
    ```

    **Preconditions of the 1st Action:**
    ```
    {preconditions_1}
    ```

    **Effects of the 1st Action:**
    ```
    {effects_1}
    ```

    **Action 2:**
    ```
    {action_2}
    ```

    **Preconditions of the 2nd Action:**
    ```
    {preconditions_2}
    ```

    **Effects of the 2nd Action:**
    ```
    {effects_2}
    ```

    Using this information, please provide a short, logical response that addresses the question.
    """

    return to_return


# if __name__ == "__main__":
#     # If running this file directly, we need to run from the root directory using the following commdand:
#     # python -m code.llm_reasoning.prompt
#     from ..templates import rdf_utils
#
#     action: str = "moveup sokoban l19 l12"
#
#     # Since the file is being run from the root directory (see the README.md in this file's directory),
#     # the path to the ontology file is correct
#     g: Graph = Graph().parse("../data/sokoban/plan-ontology-rdf-instances_sokoban.owl", format="xml")
#
#     preconditions, effects = rdf_utils.get_grounded_predicates(action, g)
#     print(f"Object: {action}\nPreconditions: {preconditions}\nEffects: {effects}\n")


class Prompt:
    """
    Class to generate prompts for reasoning with Sokoban.
    """

    def __init__(self, problem: str, solution: str, domain: str,
                 prompt_actions: dict[str, str], include_ontology: bool = False):
        """
        Initialize the problem and solution for reasoning with Sokoban.
        @param problem: The Sokoban problem in PDDL format.
        @param solution: The generated solution plan.
        @param domain: The domain of the problem.
        @param prompt_actions: The dictionary of prompt questions.
            The keys are the question types and the values are the actions. Both strings.
            Valid keys are: "Prompt 2", "Prompt 3", "Prompt 4a", "Prompt 4b", "Prompt 4c-1", "Prompt 4c-2", "Prompt 5".
            Note that prompt 1 does not have a question, since it is a validation question type.
            Note that since there are two actions for prompt 4c, it is split into two parts: 4c-1 and 4c-2.
        @param include_ontology: Whether to include the ontology in the prompt. Default is False.
        """
        self.prompt_actions = prompt_actions
        self.include_ontology = include_ontology
        self.domain = domain

        # For the problem, replace the last two character (which are "\n)") with "\n\t)"
        self.problem = problem[:-2] + "\n\t)"

        # For the solution, replace newlines with tab and newline and add a tab at the beginning
        self.solution = "\t" + solution.replace("\n", "\n\t")

    def prompt_1(self) -> str:
        """
        Generate prompt one for the reasoning with Sokoban.
        Question type: Is the plan valid?
        @return: A formatted prompt string.
        """
        return _prompt_1_template(self.problem, self.solution, self.domain, self.include_ontology)

    def prompt_2(self) -> str:
        """
        Generate prompt two for the reasoning with Sokoban.
        Question type: Why is action A used in the solution?
            Note: Here action A is the first action in the solution.
        @return: A formatted prompt string.
        """
        action: str = self.prompt_actions["Prompt 2"]

        # Get the preconditions and effects of the action
        # Since the file is being run from the root directory (see the README.md in this file's directory),
        # the path to the ontology file is correct
        preconditions, effects = rdf_utils.get_grounded_predicates(
            action, Graph().parse("../data/sokoban/plan-ontology-rdf-instances_sokoban.owl", format="xml"))

        question: str = f"Why is the action {action} used in the solution?"

        return _single_ques_template(self.problem, self.solution, question, self.domain, action,
                                     preconditions, effects, self.include_ontology)

    def prompt_3(self) -> str:
        """
        Generate prompt three for the reasoning with Sokoban.
        Question type: Why is action A used in the solution?
            Note: Here action A is the last action in the solution.
        @return: A formatted prompt string.
        """
        action: str = self.prompt_actions["Prompt 3"]

        # Get the preconditions and effects of the action
        # Since the file is being run from the root directory (see the README.md in this file's directory),
        # the path to the ontology file is correct
        preconditions, effects = rdf_utils.get_grounded_predicates(
            action, Graph().parse("../data/sokoban/plan-ontology-rdf-instances_sokoban.owl", format="xml"))

        question: str = f"Why is the action {action} used in the solution?"

        return _single_ques_template(self.problem, self.solution, question, self.domain, action,
                                     preconditions, effects, self.include_ontology)

    def prompt_4a(self) -> str:
        """
        Generate prompt 4a for the reasoning with Sokoban.
        Intent type: Why is action A used in the solution?
        @return: A formatted prompt string.
        """
        action: str = self.prompt_actions["Prompt 4a"]

        # Get the preconditions and effects of the action
        # Since the file is being run from the root directory (see the README.md in this file's directory),
        # the path to the ontology file is correct
        preconditions, effects = rdf_utils.get_grounded_predicates(
            action, Graph().parse("../data/sokoban/plan-ontology-rdf-instances_sokoban.owl", format="xml"))

        question: str = f"Why is the action {action} used in the solution?"

        return _single_ques_template(self.problem, self.solution, question, self.domain, action,
                                     preconditions, effects, self.include_ontology)

    def prompt_4b(self) -> str:
        """
        Generate prompt 4b for the reasoning with Sokoban.
        Intent type: Why is action A not used in the solution?
        @return: A formatted prompt string.
        """
        action: str = self.prompt_actions["Prompt 4b"]

        # Get the preconditions and effects of the action
        # Since the file is being run from the root directory (see the README.md in this file's directory),
        # the path to the ontology file is correct
        preconditions, effects = rdf_utils.get_grounded_predicates(
            action, Graph().parse("../data/sokoban/plan-ontology-rdf-instances_sokoban.owl", format="xml"))

        question: str = f"Why is the action {action} not used in the solution?"

        return _single_ques_template(self.problem, self.solution, question, self.domain, action,
                                     preconditions, effects, self.include_ontology)

    def prompt_4c(self) -> str:
        """
        Generate prompt 4c for the reasoning with Sokoban.
        Intent type: Why is action A used in the solution rather than action B?
        @return: A formatted prompt string.
        """
        action_1: str = self.prompt_actions["Prompt 4c-1"]
        # Get the preconditions and effects of the action
        # Since the file is being run from the root directory (see the README.md in this file's directory),
        # the path to the ontology file is correct
        preconditions_1, effects_1 = rdf_utils.get_grounded_predicates(
            action_1, Graph().parse("../data/sokoban/plan-ontology-rdf-instances_sokoban.owl", format="xml"))

        action_2: str = self.prompt_actions["Prompt 4c-2"]
        # Get the preconditions and effects of the action
        # Since the file is being run from the root directory (see the README.md in this file's directory),
        # the path to the ontology file is correct
        preconditions_2, effects_2 = rdf_utils.get_grounded_predicates(
            action_2, Graph().parse("../data/sokoban/plan-ontology-rdf-instances_sokoban.owl", format="xml"))

        question: str = f"Why is the action {action_1} used in the solution rather than action {action_2}?"

        return _double_ques_template(self.problem, self.solution, question, self.domain,
                                     action_1, preconditions_1, effects_1,
                                     action_2, preconditions_2, effects_2,
                                     self.include_ontology)

    def prompt_5(self) -> str:
        """
        Generate prompt five for the reasoning with Sokoban.
        Question type: {an out-of-scope question}
        @return: A formatted prompt string.
        """
        action: str = self.prompt_actions["Prompt 5"]

        # Get the preconditions and effects of the action
        # Since the file is being run from the root directory (see the README.md in this file's directory),
        # the path to the ontology file is correct
        preconditions, effects = rdf_utils.get_grounded_predicates(
            action, Graph().parse("../data/sokoban/plan-ontology-rdf-instances_sokoban.owl", format="xml"))

        question: str = f"Why is the action {action} used in the solution?"

        return _single_ques_template(self.problem, self.solution, question, self.domain, action,
                                     preconditions, effects, self.include_ontology)

    def get_prompts(self) -> dict[str, str]:
        """
        Get all the prompts for the reasoning with Sokoban.
        @return: A dictionary of the prompt names and their respective formatted prompt strings.
        """
        prompt_names = ["Prompt 1", "Prompt 2", "Prompt 3", "Prompt 4a", "Prompt 4b", "Prompt 4c", "Prompt 5"]
        prompts = [self.prompt_1(), self.prompt_2(), self.prompt_3(), self.prompt_4a(),
                   self.prompt_4b(), self.prompt_4c(), self.prompt_5()]
        return dict(zip(prompt_names, prompts))


def get_prompt_dict() -> dict[int, tuple[Prompt, Prompt]]:
    """
    Get the dictionary of prompts for reasoning with Sokoban from the prompts.json file.
    @return: A dictionary of the plan numbers and their respective Prompt objects.
    """

    # Read the prompts.json file and store into a list of 3-tuples
    # Define a JSON schema for validation
    # Define a JSON schema for validation
    schema = {
        "type": "object",
        "properties": {
            "prompts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string"},
                        "problem": {"type": "string"},
                        "solution": {"type": "string"},
                        "prompt_actions": {"type": "object"}
                    },
                    "required": ["domain", "problem", "solution", "prompt_actions"]
                }
            }
        },
        "required": ["prompts"]
    }

    def load_and_validate_json(file_path):
        """
        Load and validate the JSON data against the predefined schema.
        @param file_path: The path to the JSON file to be loaded.
        @return: The validated JSON data.
        @raise ValueError: If the JSON data does not conform to the schema.
        """
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Validate JSON data against the schema
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            raise ValueError(f"JSON validation error: {e.message}")

        return data

    def parse_prompts_to_list(data):
        """
        Parse the JSON data and store each prompt as a 4-tuple in a list.
        @param data: The JSON data containing prompts.
        @return: A list where each tuple contains (problem, solution, prompt_actions).
        """
        prompts = data['prompts']
        prompts_list = []

        for prompt in prompts:
            domain = prompt['domain']
            problem = prompt['problem']
            solution = prompt['solution']
            prompt_actions = prompt['prompt_actions']

            # Append the tuple (domain, problem, solution, prompt_actions) to the list
            prompts_list.append((domain, problem, solution, prompt_actions))

        return prompts_list

    plan_dict: dict[int, tuple[Prompt, Prompt]] = {}
    try:
        json_data = load_and_validate_json('prompts.json')
        prompts_list = parse_prompts_to_list(json_data)

        for idx, (domain, problem, solution, prompt_actions) in enumerate(prompts_list):
            plan_dict[idx + 1] = (
                Prompt(problem, solution, domain, prompt_actions, False),
                Prompt(problem, solution, domain, prompt_actions, True)
            )
            # Displaying the prompts list
            # print(f"Prompt {idx + 1}:")
            # print("Domain:", domain)
            # print("Problem:", problem)
            # print("Solution:", solution)
            # print("Prompt Actions:", prompt_actions)
            # print("-" * 40)

    except ValueError as e:
        print("Error:", e)

    return plan_dict

if __name__=="__main__":
    get_prompt_dict()
