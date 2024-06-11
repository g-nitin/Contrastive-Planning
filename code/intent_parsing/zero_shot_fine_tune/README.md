# Zero-Shot Fine-Tuning 

This folder contains the code to fine-tune the zero-shot classification model and test the fine-tuned model.

The files are organized as follows:

- The scripts `zero-shot-fine-tune.py` and `zero-shot-fine-tune-test.py` contain the code to fine-tune the zero-shot classification model and test the fine-tuned model, respectively.

- The zero-shot classification model tuning was done on HPC using the `slurm` job scheduler. The files `job_zero-shot.sh` and `job_zero-shot-test.sh` contain the job submission scripts for the fine-tuning and testing of the zero-shot classification model, respectively.

Lastly, the fine-tuned models can be found the [v0.1.0 release](https://github.com/g-nitin/Contrastive-Planning-NLP/releases/tag/v0.1.0) of the repository.
