#!/bin/bash
#SBATCH --partition=batch
#SBATCH --job-name=faststructure_array_K1-10
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=2-00:00:00
#SBATCH --array=1-10
#SBATCH --output=faststructure_K%a.out
#SBATCH --error=faststructure_K%a.err

# 1. Load module
module load faststructure/1.0

# 2. Variables
WORKING_DIR=/work/fauverlab/zachpella/scripts_ticks_and_onlineJune2025/combined_pop_gen/structure_files
OUTDIR=${WORKING_DIR}/faststructure_results
INPUT_FILE=${WORKING_DIR}/cohort_formatted

mkdir -p ${OUTDIR}
cd ${WORKING_DIR}

# 3. K value is just the array task ID
K=${SLURM_ARRAY_TASK_ID}

# Create unique seed for each K
SEED=$((29092025 + K))

echo "Running fastStructure for K=${K}, TaskID=${SLURM_ARRAY_TASK_ID}, Seed=${SEED}"

# 4. Run fastStructure
/util/opt/anaconda/deployed-conda-envs/packages/faststructure/envs/faststructure-1.0/bin/structure.py \
    -K ${K} \
    --input=${INPUT_FILE} \
    --output=${OUTDIR}/faststructure_K${K} \
    --format=str \
    --seed=${SEED} \
    --full

echo "Finished K=${K}"
echo "Output files: ${OUTDIR}/faststructure_K${K}.${K}.*"
