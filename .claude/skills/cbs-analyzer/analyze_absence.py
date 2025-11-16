#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pandas>=2.0.0", "scipy>=1.9.0", "pyarrow>=10.0.0"]
# ///

import pandas as pd
import json
from pathlib import Path
from scipy import stats

dataset_id = "83130NED"
base_dir = Path("/var/home/ewt/ai-skills")
df = pd.read_parquet(base_dir / "data" / dataset_id / "data.parquet")

# Load metadata
with open(base_dir / "data" / dataset_id / "metadata.json") as f:
    metadata = json.load(f)

print(f"Dataset: {metadata['title']}")
print(f"Shape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
print("\n" + "="*80 + "\n")

# Display first few rows to understand structure
print("Sample data:")
print(df.head(10))
print("\n" + "="*80 + "\n")

# Check for absence-related columns
print("Column data types:")
print(df.dtypes)
print("\n" + "="*80 + "\n")

# Find columns related to "share of absence" (likely "Aandeel verzuimd")
absence_cols = [col for col in df.columns if 'verzuim' in col.lower() or 'aandeel' in col.lower()]
print(f"Absence-related columns: {absence_cols}")
print("\n" + "="*80 + "\n")

# Filter data for 2014 and 2023
df_2014 = df[df['Perioden'] == '2014JJ00']
df_2023 = df[df['Perioden'] == '2023JJ00']

print(f"2014 data: {len(df_2014)} rows")
print(f"2023 data: {len(df_2023)} rows")
print("\n" + "="*80 + "\n")

# Display all numeric columns to identify the share of absence
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
print(f"Numeric columns: {numeric_cols}")
print("\n" + "="*80 + "\n")

# Display sample of 2014 and 2023 data
print("2014 Sample:")
print(df_2014.head())
print("\n2023 Sample:")
print(df_2023.head())
print("\n" + "="*80 + "\n")

# Assuming there's a column for share of absence, let's find it
# Common Dutch term: "Aandeel verzuimd" or similar
for col in numeric_cols:
    print(f"\n{col} statistics:")
    print(f"2014 - Mean: {df_2014[col].mean():.4f}, Median: {df_2014[col].median():.4f}, Std: {df_2014[col].std():.4f}")
    print(f"2023 - Mean: {df_2023[col].mean():.4f}, Median: {df_2023[col].median():.4f}, Std: {df_2023[col].std():.4f}")

    # Filter out NaN values for t-test
    data_2014 = df_2014[col].dropna()
    data_2023 = df_2023[col].dropna()

    if len(data_2014) > 0 and len(data_2023) > 0:
        # Perform independent samples t-test
        t_stat, p_value = stats.ttest_ind(data_2014, data_2023)

        print(f"\nT-test results for {col}:")
        print(f"  t-statistic: {t_stat:.4f}")
        print(f"  p-value: {p_value:.6f}")
        print(f"  Significant at 0.05 level: {'YES' if p_value < 0.05 else 'NO'}")

        # Calculate effect size (Cohen's d)
        pooled_std = ((len(data_2014)-1)*data_2014.std()**2 + (len(data_2023)-1)*data_2023.std()**2) / (len(data_2014) + len(data_2023) - 2)
        pooled_std = pooled_std ** 0.5
        cohens_d = (data_2014.mean() - data_2023.mean()) / pooled_std
        print(f"  Cohen's d (effect size): {cohens_d:.4f}")

        # Interpret Cohen's d
        if abs(cohens_d) < 0.2:
            effect_interpretation = "negligible"
        elif abs(cohens_d) < 0.5:
            effect_interpretation = "small"
        elif abs(cohens_d) < 0.8:
            effect_interpretation = "medium"
        else:
            effect_interpretation = "large"
        print(f"  Effect size interpretation: {effect_interpretation}")
