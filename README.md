# Enhancing Plan Explanations with Planning Ontology and Large Language Models

This repository contains the code and resources for our project on enhancing the generation of plan explanations using Planning Ontology and Large Language Models.

## Project Overview

We tackle the challenge of transparency in automated planning by introducing a novel framework designed to generate contrastive explanations for plans. Our approach leverages Planning Ontology and integrates Natural Language Processing (NLP) with SPARQL queries to provide clear and insightful explanations.

### Key Features

- Integration of Planning Ontology with AI Planning systems
- Generation of interactive plan explanations using Knowledge Graphs and Large Language Models (LLMs)
- Focus on the Sokoban domain, with potential for extension to other planning domains

## Repository Usage

This repository contains the following directories: `code`, `data`, `models`.
Please refer to the README files in each directory for detailed instructions on how to use the resources.

## Experiments

Our experiments explore different prompt structures to enhance LLM reasoning in the Sokoban domain. We focus on four key question types:

1. Plan validation
2. Action inclusion
3. Action exclusion
4. Action preference

We compare base prompts (including initial state, goal state, plan, and question) with ontology-enhanced prompts that add domain-specific constraints from the planning ontology.

## Results

- Ontology-enhanced prompts improve reasoning for smaller LLMs
- Significant performance boost observed for lower-parameter models

## Future Work

- Conduct user studies to evaluate the explanations
- Support contrastive explanations
- Explore different prompting strategies (e.g., Chain of Thought, ReAct)
- Extend the framework to other planning domains (e.g., Rubik's Cube, N-Puzzle)

## References

1. Muppasani, B., Pallagani, V., Srivastava, B. and Mutharaju, R., 2023. Building and Using a Planning Ontology from Past Data for Performance Efficiency. In PLATO@ ICAPS.
2. Muppasani, B., Pallagani, V., Srivastava, B., Mutharaju, R., Huhns, M.N. and Narayanan, V., 2023. A Planning Ontology to Represent and Exploit Planning Knowledge for Performance Efficiency. arXiv preprint arXiv:2307.13549.

## License

This repository is available under the MIT license. See the LICENSE file for more info.
