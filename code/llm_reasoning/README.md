# Reasoning through LLMs

# Sokoban Exploration

This directory contains the code for querying and reasoning with different LLMs.
The files are organized as follows:
- `reason.py`: contains the code for querying LLMs, writing the outputs and time to the `output` subdirectory, and generating the plot for the time in the `plots` subdirectory.
- `output/`: contains the output of the queries to the LLMs. The output is stored in a `.md` file with the name of the LLM in the title.
- `plots/`: contains the plots for the time taken to query the LLMs.
- `sokoban_prompt.py`: contains the code for generating different prompts for the Sokoban environment.

To run the code, you can use the following command:
```bash
  python3 reason.py
```
