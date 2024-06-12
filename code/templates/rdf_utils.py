from typing import List, Iterator
from rdflib import Graph, query
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


def get_actions_from_rdf(g: Graph, domain: str = "sokoban") -> List[query.ResultRow]:
    """
    Get the actions from an RDF graph.
    @param g: The RDF graph.
    @param domain: The domain of the actions. Default is "sokoban".
    @return: The actions from the RDF graph. Type: List[query.ResultRow]
    """

    return get_query_results(
        g,
        f"""
        PREFIX planning: <https://purl.org/ai4s/ontology/planning#>

        SELECT ?action
        WHERE {{
            planning:{domain} planning:hasAction ?action .
        }}
        """
    )


def get_preconditions_from_rdf(g: Graph, action: str) -> List[query.ResultRow]:
    """
    Get the preconditions for an action from an RDF graph.
    @param g: The RDF graph.
    @param action: The action to get the preconditions for.
    @return: The preconditions from the RDF graph. Type: List[query.ResultRow]
    """

    return get_query_results(
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


def get_effects_from_rdf(g: Graph, action: str) -> List[query.ResultRow]:
    """
    Get the effects for an action from an RDF graph.
    @param g: The RDF graph.
    @param action: The action to get the preconditions for.
    @return: The effects from the RDF graph. Type: List[query.ResultRow]
    """

    return get_query_results(
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


def get_parameters_from_rdf(g: Graph, action: str) -> List[query.ResultRow]:
    """
    Get the parameters for an action from an RDF graph.
    @param g: The RDF graph.
    @param action: The action to get the preconditions for.
    @return: The effects from the RDF graph. Type: List[query.ResultRow]
    """

    return get_query_results(
        g,
        f"""
        PREFIX planning: <https://purl.org/ai4s/ontology/planning#>

        SELECT ?param
        WHERE {{
            planning:{action} planning:hasParameter ?param .
        }}
        """
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
