from typing import List, Iterator
from rdflib import Graph, query, graph
from re import finditer, IGNORECASE, Match


def get_query_results(g: Graph, sparql_query: str) -> List[query.ResultRow]:
    """
    Execute a SPARQL query on an RDF graph and return the results.
    @param g: The RDF graph.
    @param sparql_query: The SPARQL query.
    @return: The results of the query. Type: List[query.ResultRow]
    """
    to_return: List[query.ResultRow] = []

    for r in g.query(sparql_query):
        to_return.append(r)

    return to_return


def format_query_result_a(query_output: List[query.ResultRow]) -> List[str]:
    return [str(lit[0])[1:-1] for lit in query_output]


def format_query_result_b(query_output: List[query.ResultRow]) -> List[str]:
    return [str(lit[0]).split("#")[-1] for lit in query_output]


def get_actions_from_rdf(g: Graph, domain: str) -> List[str]:
    """
    Get the actions from an RDF graph.
    @param g: The RDF graph.
    @param domain: The domain of the actions.
    @return: The actions from the RDF graph. Type: List[query.ResultRow]
    """

    return format_query_result_b(
        get_query_results(
            g,
            f"""
            PREFIX planning: <https://purl.org/ai4s/ontology/planning#>
    
            SELECT ?action
            WHERE {{
                planning:{domain} planning:hasAction ?action .
            }}
            """
        )
    )


def get_parameters_from_rdf(g: Graph, action: str) -> List[str]:
    """
    Get the parameters for an action from an RDF graph.
    @param g: The RDF graph.
    @param action: The action to get the preconditions for.
    @return: The effects from the RDF graph. Type: List[query.ResultRow]
    """

    return format_query_result_b(
        get_query_results(
            g,
            f"""
            PREFIX planning: <https://purl.org/ai4s/ontology/planning#>

            SELECT ?param
            WHERE {{
                planning:{action} planning:hasParameter ?param .
            }}
            """
        )
    )


def get_preconditions_from_rdf(g: Graph, action: str) -> List[str]:
    """
    Get the preconditions for an action from an RDF graph.
    @param g: The RDF graph.
    @param action: The action to get the preconditions for.
    @return: The preconditions from the RDF graph. Type: List[query.ResultRow]
    """

    return format_query_result_a(
        get_query_results(
            g,
            f"""
                PREFIX planning: <https://purl.org/ai4s/ontology/planning#>
                PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
        
                SELECT ?aLabel
                WHERE {{
                    planning:{action} planning:hasPrecondition ?condition .
                    ?condition rdf:label ?aLabel .
                }}
                """
        )
    )


def get_effects_from_rdf(g: Graph, action: str) -> List[str]:
    """
    Get the effects for an action from an RDF graph.
    @param g: The RDF graph.
    @param action: The action to get the preconditions for.
    @return: The effects from the RDF graph. Type: List[query.ResultRow]
    """

    return format_query_result_a(
        get_query_results(
            g,
            f"""
                PREFIX planning: <https://purl.org/ai4s/ontology/planning#>
                PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#>
                
                SELECT ?aLabel
                WHERE {{
                    planning:{action} planning:hasEffect ?effect .
                    ?effect rdf:label ?aLabel .
                }}
                """
        )
    )


def extract_grounded_objects(query: str, actions_dict: dict[str, int]) -> List[str]:
    """
    Extract grounded objects from a query based on a dictionary of actions and their parameters.
    @param query: The query to extract grounded objects from.
    @param actions_dict: A dictionary of actions and their number of parameters.
    @return: The grounded objects extracted from the query. Type List[str].
    """

    # List to hold regex patterns for all actions
    patterns: List[str] = []

    # Iterate over the actions_dict to create regex patterns
    for action, num_params in actions_dict.items():
        # Build a regex pattern for the action with the specified number of parameters
        # Assuming parameters are alphanumeric and separated by spaces
        params_pattern: str = r'\s+\w+' * num_params  # e.g., "\s+\w+" repeated num_params times
        full_pattern: str = rf'\b{action}{params_pattern}\b'
        patterns.append(full_pattern)

    # Combine all patterns into a single pattern with OR (|)
    combined_pattern: str = "|".join(patterns)

    # Find all matches in the query
    matches: Iterator[Match[str]] = finditer(combined_pattern, query, IGNORECASE)

    # Extract and return the complete matches
    return [match.group(0) for match in matches]


def extract_actions(query: str, domain: str) -> list[str]:
    """
    Given a user natural language (NL) query, extract the grounded object(s) from the user query. Some examples:
    `query`: “Why is moveLeft sokoban x1 y1 not used in the plan?”
        returned: [“moveLeft sokoban x1 y1”]
    `query`: “Why is moveLeft sokoban x1 y1 used in the plan?”
        returned: [“moveLeft sokoban x1 y1”]
    `query`: “Why is moveLeft sokoban x1 y1 used rather than moveRight sokoban x1 y1?”
        returned: [“moveLeft sokoban x1 y1”, “moveRight sokoban x1 y1”]
    Note that this function works for the Sokoban domain.

    :param query: The query to extract actions from.
    :param domain: The domain of the actions.
    :return: The list of action(s) extracted from the query.
    """
    # Create the mapping for the actions and their number of parameters
    if domain == "sokoban":
        file_path: str = "../../data/sokoban/plan-ontology-rdf-instances_sokoban.owl"
    elif domain == "blocksworld":
        file_path: str = "../../data/blocksworld/plan-ontology-rdf-instances_blocksworld.owl"
    else:
        raise ValueError(f"Invalid domain: {domain}.\nShould be either 'sokoban' or 'blocksworld'.")

    g: graph.Graph = Graph().parse(file_path, format="xml")

    # Get all actions
    actions: List[str] = get_actions_from_rdf(g, domain)

    # Create a dictionary for the actions and their number of parameters
    # Keys: actions (string); Values: number of parameters (int)
    actions_dict: dict[str, int] = {action: 0 for action in actions}

    # Get parameters for the actions
    for action in actions_dict.keys():
        parameters: List[str] = get_parameters_from_rdf(g, action)
        actions_dict[action] = len(parameters)  # Update the number of parameters

    # Extract grounded objects for each query
    return extract_grounded_objects(query, actions_dict)


def get_grounded_predicates(grounded_action: str, g: Graph) -> tuple[List[str], List[str]]:
    """
    Given a string of action, return the grounded precondition and effect predicates.
    For example, given "moveLeft sokoban x1 y1", return a tuple of the grounded predicates:
    ( ['sokoban sokoban', 'at sokoban x1', 'leftOf y1 x1', 'clear y1'],
      ['at sokoban y1', 'clear x1', 'not (at sokoban x1)', 'not (clear y1)'] )
    The lifted predicates were:
    ( ['sokoban ?sokoban', 'at ?sokoban ?x', 'leftOf ?y ?x', 'clear ?y'],
      ['at ?sokoban ?y', 'clear ?x', 'not (at ?sokoban ?x)', 'not (clear ?y)'] )

    @param grounded_action: The string object to extract predicates from.
    @param g: The RDF graph. Default is the Sokoban domain, used from the data folder.
    @return: A tuple of the grounded precondition and effect predicates. Type: tuple(List[str], List[str])
    """

    # Get the lifted action and parameters from the grounded action
    lifted_action, *params = grounded_action.split(" ")

    # Get the parameters from the lifted action
    lifted_params: List[str] = get_parameters_from_rdf(g, lifted_action.lower())

    # Get the preconditions and effects from the lifted action
    preconditions: List[str] = get_preconditions_from_rdf(g, lifted_action.lower())
    effects: List[str] = get_effects_from_rdf(g, lifted_action.lower())

    # Replace the lifted parameters with the grounded parameters in the preconditions and effects
    # One thing to take into account is that the `preconditions`/`effects` list
    # may contain more predicates than the `params` list.

    # Replace the lifted parameters with the grounded parameters in the preconditions and effects
    for param, lifted_param in zip(params, lifted_params):
        preconditions = [precondition.replace(lifted_param, param) for precondition in preconditions]
        effects = [effect.replace(lifted_param, param) for effect in effects]

    return preconditions, effects
