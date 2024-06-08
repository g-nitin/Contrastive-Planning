# Intent Parsing

This directory contains the code the intent classification of natural language queries.

The goal was to create an NLP-based framework to parse the input question to categorize the intent into one of the following question types:
1. Why is action A not used in the plan, rather than being used?
2. Why is action A used in the plan, rather than not being used?
3. Why is action A used in state S, rather than action B?

The `data` subdirectory contains the training and testing (combined into one) data for the intent classification model. The data was generated using GPT-4o from OpenAI.

The `model_testing` subdirectory contains the iPython notebooks to test different intent classification models. After testing, the zero-shot classification model was chosen for fine-tuning.

The scripts `zero-shot-fine-tune.py` and `zero-shot-fine-tune-test.py` contain the code to fine-tune the zero-shot classification model and test the fine-tuned model, respectively.

The zero-shot classification model tuning was done on HPC using the `slurm` job scheduler. The files `job_zero-shot.sh` and `job_zero-shot-test.sh` contain the job submission scripts for the fine-tuning and testing of the zero-shot classification model, respectively.

Lastly, the fine-tuned models can be found the [v0.1.0 release](https://github.com/g-nitin/Contrastive-Planning-NLP/releases/tag/v0.1.0) of the repository.

