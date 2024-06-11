# Intent Parsing

This directory contains the code the intent classification of natural language queries.

The goal was to create an NLP-based framework to parse the input question to categorize the intent into one of the following question types:
1. Why is action A not used in the plan, rather than being used?
2. Why is action A used in the plan, rather than not being used?
3. Why is action A used in state S, rather than action B?

The data used is in the `data` directory in the topmost level of this project.

The files are organized as follows:
- The `model_testing` subdirectory contains the iPython notebooks to test different intent classification models. After testing, the zero-shot classification model was chosen for fine-tuning.
- The `zero_shot_fine_tune` subdirectory contains the code to fine-tune the zero-shot classification model and test the fine-tuned model.
