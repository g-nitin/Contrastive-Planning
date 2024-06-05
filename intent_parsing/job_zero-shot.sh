#! /bin/bash

#SBATCH --job-name=zero-shot-fine-tune
#SBATCH -o r_out%j.out
#SBATCH -e r_err%j.err

#SBATCH --mail-user=niting@email.sc.edu
#SBATCH --mail-type=ALL

#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH -p v100-32gb-hiprio

#SBATCH --gres=gpu:1

module load python3/anaconda/2021.07 gcc/12.2.0 cuda/12.1
source activate /home/niting/miniconda3/envs/auto-plan

echo $CONDA_DEFAULT_ENV

#Run script
hostname
python3 zero-shot-fine-tune.py

#Exit the conda system
conda deactivate