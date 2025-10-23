#!/usr/bin/env python3
import matplotlib.pyplot as plt
import pandas as pd

# --- Config ---
K = 2
input_file = f"faststructure_K{K}.2.meanQ"
label_file = "../name_and_state_cleaned.txt"
output_pdf = f"Admixture_K{K}_custom_matplotlib.pdf"

# --- Read data ---
Q = pd.read_csv(input_file, sep=r"\s+", header=None)
labels = [line.strip() for line in open(label_file)]

# --- Custom colors for each ancestry component ---
# Change/add colors as needed; should match K
colors = ['#1f77b4', '#ff7f0e']  # Example: blue & orange

# --- Plot setup ---
fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.25), 4))  # auto-width scaling
bottom = pd.Series([0]*len(labels))

for i in range(Q.shape[1]):
    ax.bar(range(len(Q)), Q[i], bottom=bottom, color=colors[i])
    bottom += Q[i]

# --- X-axis labels ---
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=90, fontsize=6)

# --- Axis labels and title ---
ax.set_ylabel("Ancestry Proportion", fontsize=10)
ax.set_xlabel("Samples", fontsize=10)
ax.set_title(f"Admixture Plot (K={K})", fontsize=12)
ax.set_xlim(-0.5, len(labels) - 0.5)

plt.tight_layout()
plt.savefig(output_pdf, bbox_inches="tight")
print(f"✅ Plot saved to {output_pdf}")
