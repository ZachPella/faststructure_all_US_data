#!/bin/bash
#SBATCH --partition=guest
#SBATCH --job-name=faststructure_chooseK
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:30:00
#SBATCH --output=chooseK_results.out
#SBATCH --error=chooseK.err

# --- Define Paths ---
# Use the directory you confirmed you are running from
RESULTS_DIR='/work/fauverlab/zachpella/scripts_ticks_and_onlineJune2025/combined_pop_gen/structure_files/faststructure_results'
CHOOSEK_SCRIPT='/util/opt/anaconda/deployed-conda-envs/packages/faststructure/envs/faststructure-1.0/bin/chooseK.py'

# --- Execution ---

# 1. Load the faststructure module
module load faststructure/1.0

# 2. Change to the directory with the log files (CRITICAL)
cd ${RESULTS_DIR}

# 3. Define the base name of the input files.
#    This is the prefix *before* the K number and extension.
INPUT_BASE="./faststructure_K" # Use "./" to be absolutely explicit about the current directory

echo "Starting chooseK analysis from directory: $(pwd)"

# 4. Run the chooseK utility using the base file name.
# We are calling the script directly, which relies on the shebang to find the Python interpreter.
${CHOOSEK_SCRIPT} --input=${INPUT_BASE}

echo "ChooseK analysis finished."
echo "Results saved to: $(pwd)/chooseK_results.out"
