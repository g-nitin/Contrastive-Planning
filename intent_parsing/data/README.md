# Data

This directory contains the data used in the `intent_parsing` project. These are the examples and labels for the following intents:
1. Why is action A not used in the plan, rather than being used?
2. Why is action A used in the plan, rather than not being used?
3. Why is action A used in state S, rather than action B?

Currently, `sokoban_final_dataset.csv` contains grounded examples for the Sokoban domain.

The subdirectory `extra` contains extra datasets. All the csv files have been generated using the `data_generation.ipynb` file in that directory. More specifically,
- `lifted_dataset.csv` contains the lifted versions of the examples.
- `sokoban_dataset.csv` contains examples from the Sokoban domain. 
- `n_puzzle_dataset.csv` contains examples from the N-Puzzle domain.
- `rubiks_cube_dataset.csv` contains examples from the Rubik's Cube domain. 
- `freecell_dataset.csv` contains examples from the Free Cell domain. 
- `combined_dataset.csv` contains the combinations of the above files.
- `lifted_sokoban_dataset.csv` contains the combination of the lifted examples and the examples from the sokoban domain, i.e. `lifted_dataset.csv` + `sokoban_dataset.csv`.

