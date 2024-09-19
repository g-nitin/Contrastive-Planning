# Reasoning with Ontologies

This repository contains code for reasoning with ontologies. The main file is `explain.py` which contains the following command line arguments:
* `--plan_file` (required): The path to the plan file. Some sample plan files can be found in the `plans` subdirectory.
* `--domain` (required): The domain for the plan. The script, currently supports `sokoban` and `blocksworld`
* `--question` (required): The question to answer. Supported questions are of the following types:
  * Is the plan valid?
  * Why was `action A` chosen in the plan?
  * Why was `action A` not chosen in the plan?
  * Why was `action A` chosen instead of `action B` in the plan?

The script will output the answer to the question based on the plan and the domain.