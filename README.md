# fastStructure Analysis Pipeline

A complete pipeline for running fastStructure population genetic analysis and visualizing ancestry admixture results.


<img width="1716" height="502" alt="Screenshot 2025-10-21 133821" src="https://github.com/user-attachments/assets/0b1b059c-d620-463f-910a-3238970b6210" />
<img width="1662" height="513" alt="Screenshot 2025-10-21 133856" src="https://github.com/user-attachments/assets/32decaac-ef74-4fad-a00a-e7884cb6ac28" />
<img width="1877" height="412" alt="image" src="https://github.com/user-attachments/assets/b986fe4e-61f7-493d-9b61-3a7f814ee05e" />
<img width="1903" height="411" alt="image" src="https://github.com/user-attachments/assets/8393b0f0-acbb-43de-a94e-8666379fed28" />
<img width="1906" height="412" alt="image" src="https://github.com/user-attachments/assets/7ccf32ce-6d2a-4ab6-ab87-bcc8acf62787" />
<img width="915" height="290" alt="image" src="https://github.com/user-attachments/assets/a9d698c8-c0c4-44fa-a902-24fb36d962ca" />

## Overview

This pipeline performs model-based ancestry inference using fastStructure, determines optimal K values, and generates publication-quality visualizations of population structure.

## Pipeline Components

### 1. Running fastStructure (`run_faststructure.sh`)

SLURM job array script that runs fastStructure for K=1 to K=10.

**Key features:**
- Parallel execution across K values using SLURM array jobs
- Unique random seeds for reproducibility
- 32GB memory allocation per job
- Full likelihood model (`--full` flag)

**Usage:**
```bash
sbatch run_faststructure.sh
```

**Configuration:**
- Edit `WORKING_DIR` and `INPUT_FILE` paths
- Adjust `--array` range for different K values
- Modify memory/time limits as needed

**Expected output files:**
- `faststructure_K{K}.{K}.meanQ` - Admixture proportions
- `faststructure_K{K}.{K}.meanP` - Allele frequencies
- `faststructure_K{K}.{K}.log` - Marginal likelihood estimates
- `faststructure_K{K}.out/err` - Job logs

---

### 2. Choosing Optimal K (`chooseK.py`)

Determines the best K value using two complementary approaches:

**Approach 1: Maximum Marginal Likelihood**
- Parses converged marginal likelihood values from log files
- Identifies K that maximizes model fit

**Approach 2: Model Components (Modal K)**
- Analyzes admixture proportions (Q matrices)
- Counts components explaining N-1 individuals
- Reports most frequent K across runs

**Usage:**
```bash
python chooseK.py --input=faststructure_K
```

**Output example:**
```
Model complexity that maximizes marginal likelihood = 5
Model components used to explain structure in data (modal bestK) = 4
```

---

### 3. Extracting Metrics (`extract_metrics.py`)

Compiles K, marginal likelihood (LLBO), and estimated components (K_φ*) into a single data file for plotting.

**Usage:**
```bash
python extract_metrics.py
```

**Output:**
- `k_metrics_data.txt` - CSV with columns: K, LLBO_Value, K_Phi_Star

---

### 4. Plotting Model Selection Metrics (`plot_metrics.py`)

Generates two diagnostic plots for K selection:

**Plot 1: LLBO vs. K**
- Shows marginal likelihood across K values
- Highlights K with maximum LLBO

**Plot 2: K_φ* vs. K**
- Estimated optimal components vs. assumed K
- Includes K=K reference line
- Plateau indicates true K

**Usage:**
```bash
python plot_metrics.py
```

**Output:**
- `LLBO_vs_K.png`
- `K_phi_star_vs_K.png`

---

### 5. Admixture Visualization

Two plotting scripts for visualizing ancestry proportions:

#### Basic Plot (`plot_stacked_bars.py`)
Simple stacked bar plot with sample labels.

**Usage:**
```bash
python3 plot_stacked_bars.py
```

**Configuration:** Edit K value and file paths in script header.

#### Advanced Geographic Plot (`plot_tight_stacked_bars.py`)

**Features:**
- Groups samples by U.S. state
- Custom geographic ordering (Northeast → Midwest → Plains → South)
- Nebraska samples sorted by internal prefixes (Win, FL, TR, Schram, CH)
- Group separation lines and labels
- Ultra-wide format for detailed inspection

**Usage:**
```bash
python3 plot_tight_stacked_bars.py <K>
```

**Example:**
```bash
python3 plot_tight_stacked_bars.py 5
```

**Requirements:**
- `../name_and_state_cleaned.txt` - Sample labels with state suffixes (e.g., `Sample_Nebraska`)
- Format: `SampleID_State` (handles two-word states like "North Carolina")

**Output:**
- `Admixture_K{K}_State_Final_Order.pdf`

---

## Installation Requirements

```bash
# Python packages
pip install numpy pandas matplotlib

# fastStructure (via conda or module system)
module load faststructure/1.0
```

---

## Typical Workflow

1. **Run fastStructure for multiple K values:**
   ```bash
   sbatch run_faststructure.sh
   ```

2. **Determine optimal K:**
   ```bash
   python chooseK.py --input=faststructure_K
   ```

3. **Generate diagnostic plots:**
   ```bash
   python extract_metrics.py
   python plot_metrics.py
   ```

4. **Visualize admixture for chosen K:**
   ```bash
   python3 plot_tight_stacked_bars.py 5
   ```

---

## Input Data Format

**fastStructure input:** Structure format (`.str` file)
- Columns: Sample ID, Population, Marker genotypes
- See fastStructure documentation for formatting details

**Label file:** Plain text, one sample per line
- Must match order of samples in `.meanQ` files
- Format: `SampleName_State` for geographic grouping

---

## Troubleshooting

**"No log files found"**
- Check `--input` filetag matches output prefix from `run_faststructure.sh`

**"K value extraction does not match Marginal Likelihood extractions"**
- Verify log files contain "Marginal Likelihood = " lines
- Check filename pattern matches `K(\d+)\.\d+\.log`

**"# of labels does not match # of samples"**
- Ensure label file has exactly one line per sample in `.meanQ` file

**Empty or incorrect plots**
- Run `extract_metrics.py` before `plot_metrics.py`
- Verify `k_metrics_data.txt` exists and contains data

---

## Citation

If using fastStructure, please cite:
> Raj A, Stephens M, Pritchard JK. (2014) fastSTRUCTURE: Variational Inference of Population Structure in Large SNP Data Sets. Genetics 197(2):573-589.

---

## License

Scripts provided as-is for academic research use.
