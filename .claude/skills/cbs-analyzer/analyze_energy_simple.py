#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pandas>=2.0.0", "pyarrow>=10.0.0"]
# ///

import pandas as pd
import json
from pathlib import Path

dataset_id = "83140NED"
base_dir = Path("/var/home/ewt/ai-skills/.claude/skills/cbs-analyzer")
df = pd.read_parquet(base_dir / "data" / dataset_id / "data.parquet")

# Extract year from period
df['Year'] = df['Perioden'].str[:4].astype(int)

# Strip whitespace from energy carrier codes
df['Energiedragers'] = df['Energiedragers'].str.strip()

# Key energy sources to track (main categories)
energy_sources = {
    'E006459': 'Coal and Coal Products',
    'E007215': 'Oil and Oil Products',
    'E006560': 'Natural Gas',
    'E006565': 'Renewable Energy',
}

# Use TotaalAanbodTPES_1 (Total Primary Energy Supply)
energy_col = 'TotaalAanbodTPES_1'

# Get data for each energy source
print("="*80)
print("MAJOR ENERGY SOURCES OVER TIME")
print("="*80)
print(f"\nUsing column: {energy_col} (Total Primary Energy Supply)")
print("\n")

data_by_source = {}
for code, name in energy_sources.items():
    source_data = df[df['Energiedragers'] == code][['Year', energy_col]].copy()
    source_data = source_data.sort_values('Year')
    source_data = source_data.dropna(subset=[energy_col])

    if not source_data.empty:
        data_by_source[name] = source_data.set_index('Year')[energy_col]
        print(f"{name}:")
        print(f"  Data from {source_data['Year'].min()} to {source_data['Year'].max()}")
        print(f"  Peak: {source_data[energy_col].max():.1f} PJ in {source_data.loc[source_data[energy_col].idxmax(), 'Year']}")
        print()

# Create combined DataFrame
combined = pd.DataFrame(data_by_source)
combined = combined.sort_index()

print("\n" + "="*80)
print("ENERGY CROSSOVER POINTS")
print("="*80 + "\n")

# Find crossover points
sources = list(data_by_source.keys())
for i, source1 in enumerate(sources):
    for source2 in sources[i+1:]:
        # Get common years
        comparison = combined[[source1, source2]].dropna()

        if len(comparison) > 1:
            # Track which source is dominant
            comparison['dominant'] = comparison.apply(
                lambda row: source1 if row[source1] > row[source2] else source2, axis=1
            )

            # Find where dominant source changes
            comparison['shift'] = comparison['dominant'] != comparison['dominant'].shift()

            crossovers = comparison[comparison['shift'] == True]

            if len(crossovers) > 0:
                print(f"\n{source1} vs {source2}:")
                print("-" * 60)

                for year in crossovers.index[1:]:  # Skip first row (always True)
                    prev_year = year - 1
                    if prev_year in comparison.index:
                        val1_prev = comparison.loc[prev_year, source1]
                        val2_prev = comparison.loc[prev_year, source2]
                        val1_curr = comparison.loc[year, source1]
                        val2_curr = comparison.loc[year, source2]

                        winner = comparison.loc[year, 'dominant']
                        loser = source2 if winner == source1 else source1

                        print(f"  {year}: {winner} overtook {loser}")
                        print(f"    {prev_year}: {source1}={val1_prev:.1f} PJ, {source2}={val2_prev:.1f} PJ")
                        print(f"    {year}: {source1}={val1_curr:.1f} PJ, {source2}={val2_curr:.1f} PJ")
                        print()

# Show detailed timeline
print("\n" + "="*80)
print("DETAILED TIMELINE (Selected Years)")
print("="*80 + "\n")

years_to_show = [1946, 1950, 1960, 1970, 1975, 1980, 1990, 2000, 2010, 2015, 2020, 2023, 2024]
timeline = combined.loc[combined.index.isin(years_to_show)].copy()

if not timeline.empty:
    # Add dominant source column
    timeline['Dominant Source'] = timeline.idxmax(axis=1)

    print(timeline.round(1).to_string())

# Summary statistics
print("\n" + "="*80)
print("SUMMARY")
print("="*80 + "\n")

for source in sources:
    if source in combined.columns:
        data = combined[source].dropna()
        if len(data) > 0:
            print(f"{source}:")
            print(f"  First year: {data.index.min()} ({data.iloc[0]:.1f} PJ)")
            print(f"  Peak year: {data.idxmax()} ({data.max():.1f} PJ)")
            print(f"  Latest year: {data.index.max()} ({data.iloc[-1]:.1f} PJ)")
            print(f"  Change: {((data.iloc[-1] / data.iloc[0]) - 1) * 100:+.1f}%")
            print()
