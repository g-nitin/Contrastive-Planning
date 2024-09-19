# Sokoban Exploration

This directory contains the code for the Sokoban environment and the exploration of the environment.
The files are organized as follows:
- `sokoban.pddl`: Contains the Sokoban environment.
- `sokoban_explore.ipynb`: Contains the code for the exploration of the Sokoban environment using the RDFLib library.
- `sokoban_triplets.txt`: Contains the triplets extracted from the Sokoban environment using the RDFLib library. See `sokoban_explore.ipynb` for more details. 
- `object_extraction.ipynb`: Contains the code for extracting the objects from a Natural Language query and getting results from the Sokoban environment.

The Sokoban environment is a grid-based environment where the agent has to push boxes to the goal locations. The environment is represented using the PDDL language. The exploration of the environment is done using the RDFLib library, which allows us to extract triplets from the environment.