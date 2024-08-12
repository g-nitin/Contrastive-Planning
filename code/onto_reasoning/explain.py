import rdflib
import argparse
from os import path as os_path
from sys import path as sys_path
import logging

# Need to add the parent directory to the sys path to import the rdf_utils & intent_utils module
#   More info: https://sentry.io/answers/import-files-from-a-different-folder-in-python/
sys_path.insert(1, "/".join(os_path.realpath(__file__).split("/")[0:-2]))
from templates.rdf_utils import extract_actions
from templates.intent_utils import get_intent


def load_ontology(file_path):
    g = rdflib.Graph()
    g.parse(file_path, format="xml")
    return g


def print_all_action_templates(g):
    query = """
    PREFIX planning: <https://purl.org/ai4s/ontology/planning#>
    SELECT ?action ?template
    WHERE {
        ?action a planning:DomainAction ;
                planning:hasNLTemplate ?template .
    }
    """
    results = g.query(query)
    for row in results:
        print(f"Action: {row.action}, Template: {row.template}")


def get_action_template(g, action):
    action_str = f"https://purl.org/ai4s/ontology/planning#{action.split()[0]}"
    logger.info(f"Querying for action: {action_str}")

    query = f"""
    PREFIX planning: <https://purl.org/ai4s/ontology/planning#>
    SELECT ?actionTemplate
    WHERE {{
        ?action a planning:DomainAction ;
                planning:hasNLTemplate ?actionTemplate .
        FILTER(str(?action) = '{action_str}')
    }}
    """

    results = g.query(query)
    logger.info(f"Query results: {list(results)}")

    return next(iter(results), [None])[0]

def get_preconditions(g, action):
    action_str = f"https://purl.org/ai4s/ontology/planning#{action.split()[0]}"
    logger.info(f"Querying for preconditions of action: {action_str}")

    query = f"""
    PREFIX planning: <https://purl.org/ai4s/ontology/planning#>
    SELECT ?preconditionTemplate
    WHERE {{
        ?action a planning:DomainAction ;
                planning:hasPrecondition ?precondition .
        ?precondition planning:hasNLTemplate ?preconditionTemplate .
        FILTER(str(?action) = '{action_str}')
    }}
    """

    results = g.query(query)
    logger.info(f"Query results: {list(results)}")

    return [str(row[0]) for row in results]

def get_effects(g, action):
    action_str = f"https://purl.org/ai4s/ontology/planning#{action.split()[0]}"
    logger.info(f"Querying for effects of action: {action_str}")

    query = f"""
    PREFIX planning: <https://purl.org/ai4s/ontology/planning#>
    SELECT ?effectTemplate
    WHERE {{
        ?action a planning:DomainAction ;
                planning:hasEffect ?effect .
        ?effect planning:hasNLTemplate ?effectTemplate .
        FILTER(str(?action) = '{action_str}')
    }}
    """

    results = g.query(query)
    logger.info(f"Query results: {list(results)}")

    return [str(row[0]) for row in results]


def generate_explanation(g, action, in_plan):
    action_template = get_action_template(g, action)
    preconditions = get_preconditions(g, action)
    effects = get_effects(g, action)

    explanation = f"Action: {action_template}"
    explanation += "\nPreconditions:\n" + "\n".join(f"- {p}" for p in preconditions)
    explanation += "\nEffects:\n" + "\n".join(f"- {e}" for e in effects)

    if in_plan:
        explanation += "\nThis action is used in the plan because its preconditions are met and its effects are necessary for achieving the goal."
    else:
        explanation += "\nThis action is not used in the plan because either its preconditions are not met or its effects are not necessary for achieving the goal."

    return explanation


def compare_actions(g, action1, action2):
    explanation1 = generate_explanation(g, action1, True)
    explanation2 = generate_explanation(g, action2, False)

    comparison = f"Comparison between {action1} and {action2}:\n\n"
    comparison += f"{action1}:\n{explanation1}\n\n"
    comparison += f"{action2}:\n{explanation2}\n\n"
    comparison += f"The plan uses {action1} instead of {action2} because it better fits the current state and goal of the problem."

    return comparison


def main(plan_file, question):
    ontology_file = "../../data/sokoban/plan-ontology-rdf-instances_sokoban.owl"
    logger.info(f"Loading ontology from {ontology_file}")

    g = load_ontology(ontology_file)
    logger.info(f"Ontology loaded successfully with {len(g)} triples.")

    intent, intent_num = get_intent(question)
    logger.info(f"Detected intent: {intent}")

    actions = extract_actions(question)
    logger.info(f"Extracted actions: {actions}")

    # print_all_action_templates(g)

    with open(plan_file, 'r') as f:
        plan = [line.strip() for line in f.readlines()]

    if intent_num == 1:  # Why is action A not used in the plan?
        action = actions[0]
        explanation = generate_explanation(g, action, False)
        print(explanation)

    elif intent_num == 2:  # Why is action A used in the plan?
        action = actions[0]
        if any(action in step for step in plan):
            explanation = generate_explanation(g, action, True)
            print(explanation)
        else:
            print(f"The action {action} is not used in the given plan.")

    elif intent_num == 3:  # Why is action A used rather than action B?
        action1, action2 = actions
        comparison = compare_actions(g, action1, action2)
        print(comparison)

    else:
        print("Invalid question type.")


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)  # TO ENABLE LOGGING
    logging.basicConfig(level=logging.CRITICAL)  # TO DISABLE LOGGING
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Process a plan file and answer a question.")
    parser.add_argument("plan_file", type=str, help="The path to the plan file")
    parser.add_argument("question", type=str, help="The question to answer")

    args = parser.parse_args()

    main(args.plan_file, args.question)
