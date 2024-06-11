# Data

This directory contains the data used for project. 

Currently, the data in the folder is more training and testing (combined into one) data for the intent classification models (see the `code/intent_parsing` directory). The following intents are used:
1. Why is action A not used in the plan, rather than being used?
2. Why is action A used in the plan, rather than not being used?
3. Why is action A used in state S, rather than action B?

The data was generated using GPT-4o from OpenAI.

Since the project focuses, primarily, on the Sokoban domain, the `sokoban` folder contains the data for the Sokoban domain. The `extra` folder contains data for other domains, such as the N-Puzzle, Rubik's Cube, and Free Cell domains.

The `sokoban` folder contains the following files:
- `sokoban_final_grounded_dataset.csv` contains grounded examples for the Sokoban domain.
- `sokoban_final_lifted_dataset.csv` contains lifted examples for the same domain.

The subdirectory `extra` contains extra datasets. All the csv files have been generated using the `data_generation.ipynb` file in that directory. More specifically,
- `lifted_dataset.csv` contains the lifted versions of the examples.
- `sokoban_dataset.csv` contains examples from the Sokoban domain. 
- `n_puzzle_dataset.csv` contains examples from the N-Puzzle domain.
- `rubiks_cube_dataset.csv` contains examples from the Rubik's Cube domain. 
- `freecell_dataset.csv` contains examples from the Free Cell domain. 
- `combined_dataset.csv` contains the combinations of the above files.
- `lifted_sokoban_dataset.csv` contains the combination of the lifted examples and the examples from the sokoban domain, i.e. `lifted_dataset.csv` + `sokoban_dataset.csv`.
