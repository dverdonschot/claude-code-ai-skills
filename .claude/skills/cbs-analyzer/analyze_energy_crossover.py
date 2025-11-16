#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pandas>=2.0.0", "pyarrow>=10.0.0", "matplotlib>=3.0.0"]
# ///

import pandas as pd
import json
from pathlib import Path
import matplotlib.pyplot as plt

dataset_id = "83140NED"
base_dir = Path("/var/home/ewt/ai-skills/.claude/skills/cbs-analyzer")
df = pd.read_parquet(base_dir / "data" / dataset_id / "data.parquet")

# Load metadata
with open(base_dir / "data" / dataset_id / "metadata.json") as f:
    metadata = json.load(f)

print(f"Dataset: {metadata['title']}")
print(f"Shape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
print("\n" + "="*80 + "\n")

# Extract year from period
df['Year'] = df['Perioden'].str[:4].astype(int)

# Look at the data structure
print("Sample data:")
print(df.head(20))
print("\n" + "="*80 + "\n")

# Check unique energy carriers
print("Unique energy carriers (first 20):")
print(df['Energiedragers'].unique()[:20])
print(f"\nTotal unique energy carriers: {df['Energiedragers'].nunique()}")
print("\n" + "="*80 + "\n")

# Key energy sources to track
energy_sources = {
    'E006459': 'Coal (Totaal kool)',
    'E007215': 'Oil (Aardolie)',
    'E006560': 'Natural Gas (Aardgas)',
    'E006565': 'Renewable Energy',
    'E006588': 'Wind Energy',
    'E006589': 'Solar Energy',
}

# Find columns that represent energy consumption/supply
# Let's look at numeric columns
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
print(f"Numeric columns: {numeric_cols}")
print("\n" + "="*80 + "\n")

# Display a sample with specific energy carriers
for code, name in energy_sources.items():
    sample = df[df['Energiedragers'] == code].head(3)
    if not sample.empty:
        print(f"\n{name} ({code}) sample:")
        print(sample[['Year', 'Energiedragers'] + numeric_cols[:5]])

print("\n" + "="*80 + "\n")

# Let's find the column that represents primary energy supply/consumption
# Usually the first numeric column or one with "Aanbod" or "Verbruik" in name
print("Looking for energy consumption/supply columns...")

# Get data for major energy sources over time
results = []

for code, name in energy_sources.items():
    source_data = df[df['Energiedragers'] == code].copy()
    source_data = source_data.sort_values('Year')

    if not source_data.empty:
        print(f"\n{name} ({code}):")
        print(f"  Years covered: {source_data['Year'].min()} - {source_data['Year'].max()}")
        print(f"  Total rows: {len(source_data)}")

        # Try to find the main energy value column
        # Look for columns with high values (likely in PJ - petajoules)
        for col in numeric_cols:
            if col != 'Year':
                values = source_data[col].dropna()
                if len(values) > 0:
                    max_val = values.max()
                    min_val = values.min()
                    if max_val > 10:  # Likely a meaningful energy value
                        print(f"  {col}: min={min_val:.1f}, max={max_val:.1f}")

                        # Store for analysis
                        for _, row in source_data.iterrows():
                            if pd.notna(row[col]):
                                results.append({
                                    'Year': row['Year'],
                                    'Source': name,
                                    'Code': code,
                                    'Column': col,
                                    'Value': row[col]
                                })

print("\n" + "="*80 + "\n")

# Convert to DataFrame for easier analysis
if results:
    results_df = pd.DataFrame(results)
    print(f"Total data points collected: {len(results_df)}")
    print(f"\nColumns found: {results_df['Column'].unique()}")

    # Focus on a specific column (likely the first/main one)
    # Let's use the column that appears most frequently
    main_column = results_df['Column'].value_counts().index[0]
    print(f"\nUsing main column: {main_column}")

    # Filter to just this column
    main_data = results_df[results_df['Column'] == main_column].copy()

    # Pivot to compare sources over time
    pivot = main_data.pivot(index='Year', columns='Source', values='Value')
    print("\nEnergy by source over time (sample):")
    print(pivot.head(10))
    print("\n...")
    print(pivot.tail(10))

    print("\n" + "="*80 + "\n")
    print("CROSSOVER ANALYSIS:")
    print("="*80 + "\n")

    # Find crossover points between major sources
    sources_list = pivot.columns.tolist()

    for i, source1 in enumerate(sources_list):
        for source2 in sources_list[i+1:]:
            # Find where source1 and source2 cross
            common_years = pivot[[source1, source2]].dropna()

            if len(common_years) > 1:
                # Find where one overtakes the other
                common_years['diff'] = common_years[source1] - common_years[source2]
                common_years['sign'] = common_years['diff'].apply(lambda x: 1 if x > 0 else -1)
                common_years['sign_change'] = common_years['sign'].diff()

                crossovers = common_years[common_years['sign_change'] != 0]

                if len(crossovers) > 0:
                    print(f"\n{source1} vs {source2}:")
                    for year in crossovers.index:
                        prev_year = year - 1
                        if prev_year in common_years.index:
                            val1_prev = common_years.loc[prev_year, source1]
                            val2_prev = common_years.loc[prev_year, source2]
                            val1_curr = common_years.loc[year, source1]
                            val2_curr = common_years.loc[year, source2]

                            if val1_prev < val2_prev and val1_curr > val2_curr:
                                print(f"  {year}: {source1} overtook {source2}")
                                print(f"    {prev_year}: {source1}={val1_prev:.1f}, {source2}={val2_prev:.1f}")
                                print(f"    {year}: {source1}={val1_curr:.1f}, {source2}={val2_curr:.1f}")
                            elif val1_prev > val2_prev and val1_curr < val2_curr:
                                print(f"  {year}: {source2} overtook {source1}")
                                print(f"    {prev_year}: {source1}={val1_prev:.1f}, {source2}={val2_prev:.1f}")
                                print(f"    {year}: {source1}={val1_curr:.1f}, {source2}={val2_curr:.1f}")

    # Create visualization
    print("\n" + "="*80 + "\n")
    print("Creating visualization...")

    plt.figure(figsize=(14, 8))
    for source in pivot.columns:
        if pivot[source].notna().sum() > 0:
            plt.plot(pivot.index, pivot[source], marker='o', label=source, linewidth=2)

    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Energy (PJ)', fontsize=12)
    plt.title('Energy Sources Over Time (Netherlands)', fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output_path = base_dir / "energy_crossover.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Chart saved to: {output_path}")
