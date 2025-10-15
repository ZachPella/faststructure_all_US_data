#!/bin/bash
#SBATCH --partition=guest
#SBATCH --job-name=faststructure_plot_K2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:30:00
#SBATCH --output=plot_K2.out
#SBATCH --error=plot_K2.err

# 1. Load the faststructure module
module load faststructure/1.0

# 2. **CRITICAL FIX: Set the backend to 'Agg' to prevent the DISPLAY error.**
export MPLBACKEND=Agg

# 3. Define the path to the fastStructure plotting utility
DISTRICT_SCRIPT='/util/opt/anaconda/deployed-conda-envs/packages/faststructure/envs/faststructure-1.0/bin/distruct.py'

# 4. SET THE OPTIMAL K
K_TO_PLOT=2

# 5. Define the base name and output files (Corrected to 'faststructure_K2')
INPUT_BASE="faststructure_K${K_TO_PLOT}"
OUTPUT_PDF="Admixture_Plot_K${K_TO_PLOT}.pdf"

echo "Plotting results for K=${K_TO_PLOT}"

# 6. Run the plotting utility
/util/opt/anaconda/deployed-conda-envs/packages/faststructure/envs/faststructure-1.0/bin/distruct.py \
    --input=${INPUT_BASE} \
    --output=${OUTPUT_PDF} \
    -K ${K_TO_PLOT}

echo "Plot finished. Output file: $(pwd)/${OUTPUT_PDF}"
