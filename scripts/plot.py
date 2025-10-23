#!/usr/bin/env python3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import os
import re

# --- Configuration using Command Line Arguments ---
if len(sys.argv) < 2:
    print("Usage: python3 plot_county.py <K_value>")
    print("Example: python3 plot_county.py 2")
    sys.exit(1)

try:
    K = int(sys.argv[1])
except ValueError:
    print("Error: K_value must be an integer.")
    sys.exit(1)

# File names
# 🚨 CORRECTED INPUT FILE NAME FOR FASTSTRUCTURE
input_file = f"faststructure_K{K}.{K}.meanQ"
label_file = "name_and_state_county.txt"
output_pdf = f"Admixture_County_Order_K{K}.pdf"

# --- 1. Read Q-matrix from .meanQ file ---
print(f"Reading Q-matrix from: {input_file} (K={K}).")

try:
    # Read the Q-matrix (faststructure output is a simple space-separated matrix)
    Q = pd.read_csv(input_file, sep='\s+', header=None)

    # Validate that the number of columns matches K
    if Q.shape[1] != K:
        raise Exception(f"Expected {K} columns in Q-matrix but found {Q.shape[1]}. Check K value or file integrity.")

    print(f"Successfully read Q-data for {len(Q)} samples.")

except FileNotFoundError:
    # This is the expected error you were seeing, now it targets the correct file
    print(f"Error: Input file not found: {input_file}")
    sys.exit(1)
except Exception as e:
    print(f"Error reading Q-matrix: {e}")
    sys.exit(1)

# ----------------------------------------------------------------------
# --- 2. Read Labels and Validate ---
# ----------------------------------------------------------------------
try:
    labels = [line.strip() for line in open(label_file)]

    if len(labels) != len(Q):
        print(f"Error: # of labels ({len(labels)}) does not match # of samples in Q-matrix ({len(Q)}). Cannot plot.")
        sys.exit(1)

except FileNotFoundError:
    print(f"Error: Label file not found: {label_file}")
    sys.exit(1)

# ----------------------------------------------------------------------
# --- 2.5 Grouping and Sorting Data (FINAL COUNTY ORDER) ---
# ----------------------------------------------------------------------
print("Grouping and sorting samples by County/State...")

# GROUP_ORDER: Iowa -> NE Counties (Thurston, Dodge, Douglas, Sarpy) -> Kansas
GROUP_ORDER = [
    'Iowa',
    'Nebraska_Thurston',
    'Nebraska_Dodge',
    'Nebraska_Douglas',
    'Nebraska_Sarpy',
    'Kansas',
    'Other'
]

def get_group(label):
    """Function to extract the County (NE) or State (IA/KS) for grouping."""

    # Check for state-level groups
    if 'Iowa' in label:
        return 'Iowa'
    elif 'Kansas' in label:
        return 'Kansas'

    # Check for Nebraska counties (based on your dataset structure)
    if 'Sarpy' in label:
        return 'Nebraska_Sarpy'
    elif 'Dodge' in label:
        return 'Nebraska_Dodge'
    elif 'Douglas' in label:
        return 'Nebraska_Douglas'
    elif 'Thurston' in label:
        return 'Nebraska_Thurston'

    # Fallback
    return 'Other'

# 1. Create a DataFrame for labels and their assigned groups
sample_info = pd.DataFrame({
    'label': labels,
    'group': [get_group(l) for l in labels],
    'original_index': range(len(labels))
})

# 2. Assign a numerical sort key based on GROUP_ORDER
group_to_key = {group: i for i, group in enumerate(GROUP_ORDER)}
sample_info['sort_key'] = sample_info['group'].map(group_to_key).fillna(len(GROUP_ORDER))

# 3. Sort the sample info DataFrame
sample_info_sorted = sample_info.sort_values(by=['sort_key', 'label']).reset_index(drop=True)

# 4. Reorder the Q-matrix and the labels list
new_indices = sample_info_sorted['original_index'].tolist()
Q = Q.iloc[new_indices, :]
labels = sample_info_sorted['label'].tolist()
groups_sorted = sample_info_sorted['group'].tolist()
print(f"Successfully grouped and reordered {len(Q)} samples.")

# ----------------------------------------------------------------------
# --- 3. Plotting the Stacked Bars (Multi-Level Labeling) ---
# ----------------------------------------------------------------------

# 1. Setup Figure
custom_colors = plt.cm.tab10.colors[:K]
fig, ax = plt.subplots(figsize=(10, 6))
bottom = np.zeros(len(Q))

# 2. Plot Bars
for i in range(K):
    ax.bar(range(len(Q)), Q.iloc[:, i], bottom=bottom, color=custom_colors[i], width=1.0)
    bottom += Q.iloc[:, i]

# 3. Add Group Separation Lines and Labels
group_annotations = []
nebraska_groups = ['Nebraska_Thurston', 'Nebraska_Dodge', 'Nebraska_Douglas', 'Nebraska_Sarpy']
group_start_index = 0
current_group = groups_sorted[0]

# Iterate through samples to find group changes, draw lines, and store labels
for i in range(1, len(groups_sorted)):
    next_group = groups_sorted[i]

    if next_group != current_group:

        # A. Draw the separation line
        ax.axvline(x=i - 0.5, color='black', linestyle='-', linewidth=2.5, zorder=2)

        # B. Store the group label and its center for later plotting
        group_end_index = i
        group_center = (group_start_index + group_end_index - 1) / 2

        group_annotations.append({'center': group_center, 'label': current_group.replace('_', ' ')})

        # Reset for the next group
        current_group = next_group
        group_start_index = i

# Process the last group
group_center = (group_start_index + len(groups_sorted) - 1) / 2
group_annotations.append({'center': group_center, 'label': current_group.replace('_', ' ')})


# 4. Draw the Multi-Layered Group Labels

# Identify Nebraska sub-groups and non-Nebraska groups
nebraska_centers = [a['center'] for a in group_annotations if a['label'].startswith('Nebraska')]
non_nebraska_groups = [a for a in group_annotations if not a['label'].startswith('Nebraska')]

if nebraska_centers:
    # Calculate center for the top-level "Nebraska" label
    nebraska_center_x = (min(nebraska_centers) + max(nebraska_centers)) / 2

    # Draw the main "Nebraska" label (highest level)
    ax.text(
        nebraska_center_x,
        1.15, # Highest position
        "Nebraska",
        ha='center',
        va='bottom',
        fontsize=11,
        fontweight='bold',
        transform=ax.get_xaxis_transform()
    )

    # Draw the Nebraska County labels (mid-level)
    for a in [a for a in group_annotations if a['label'].startswith('Nebraska')]:
        # Extract just the County name for cleaner look
        county_name = a['label'].split(' ')[1]
        ax.text(
            a['center'],
            1.08, # Mid position
            county_name,
            ha='center',
            va='bottom',
            fontsize=8,
            fontweight='bold',
            transform=ax.get_xaxis_transform()
        )

# Draw the non-Nebraska labels (Iowa, Kansas, etc.)
for a in non_nebraska_groups:
    # Use the full group name (Iowa, Kansas, Other)
    ax.text(
        a['center'],
        1.15, # Same height as top-level Nebraska label
        a['label'],
        ha='center',
        va='bottom',
        fontsize=11,
        fontweight='bold',
        transform=ax.get_xaxis_transform()
    )

# 5. Axis Configuration
ax.set_xticks(range(len(labels)))
# Use smaller font size for dense sample labels
ax.set_xticklabels(labels, rotation=90, fontsize=4, ha='right')

ax.set_ylabel("Ancestry Proportion", fontsize=10)
ax.set_xlabel("Samples (Sorted by County/State)", fontsize=10)
ax.set_title(f"Admixture Plot (K={K}) - Grouped by County/State", fontsize=12, y=1.25)
ax.set_xlim(-0.5, len(Q) - 0.5)
ax.set_ylim(0, 1.0)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.tick_params(axis='y', labelsize=8)

# Adjust bottom margin to ensure rotated labels fit
plt.subplots_adjust(bottom=0.25)

plt.savefig(output_pdf, bbox_inches="tight")
print(f"✅ Labeled and Grouped Plot saved to {output_pdf}")
