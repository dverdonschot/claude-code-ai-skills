#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pandas>=2.0.0", "pyarrow>=10.0.0"]
# ///

import pandas as pd
import json
from pathlib import Path

dataset_id = "85524NED"
base_dir = Path("/var/home/ewt/ai-skills/.claude/skills/cbs-analyzer")
df = pd.read_parquet(base_dir / "data" / dataset_id / "data.parquet")

# Load metadata
with open(base_dir / "data" / dataset_id / "metadata.json") as f:
    metadata = json.load(f)

print(f"Dataset: {metadata['title']}")
print(f"Period: {metadata.get('total_rows_available', 'N/A')} years of data")
print(f"\nShape: {df.shape}")
print("\n" + "="*80 + "\n")

# Extract year
df['Year'] = df['Perioden'].str[:4].astype(int)

# Filter for 2010-2025
df_recent = df[df['Year'].between(2010, 2025)].copy()
df_recent = df_recent.sort_values('Year')

print(f"Data for 2010-2025: {len(df_recent)} rows")
print(f"Years: {sorted(df_recent['Year'].unique())}")
print("\n" + "="*80 + "\n")

# Find key columns - births and deaths
print("Column search - looking for births and deaths columns:")
birth_cols = [col for col in df.columns if 'geboren' in col.lower() or 'geboorte' in col.lower()]
death_cols = [col for col in df.columns if 'overleden' in col.lower() or 'sterfte' in col.lower()]
migration_cols = [col for col in df.columns if 'migratie' in col.lower() or 'immigratie' in col.lower()]

print(f"\nBirth columns ({len(birth_cols)}):")
for col in birth_cols[:10]:
    print(f"  - {col}")

print(f"\nDeath columns ({len(death_cols)}):")
for col in death_cols[:10]:
    print(f"  - {col}")

print(f"\nMigration columns ({len(migration_cols)}):")
for col in migration_cols[:10]:
    print(f"  - {col}")

print("\n" + "="*80 + "\n")

# Main summary for 2010-2025
print("POPULATION DEVELOPMENT OVERVIEW 2010-2025")
print("="*80 + "\n")

# Key metrics - try common column names
key_metrics = {
    'Live Births': ['Levendgeborenen_1', 'LevengGeborenKinderen_9'],
    'Deaths': ['Overledenen_2', 'OverledenPersonen_11'],
    'Immigration': ['Immigratie_18', 'Vestiging_14'],
    'Emigration': ['Emigratie_19', 'Vertrek_15'],
    'Population (Jan 1)': ['BevolkingOp1Januari_3', 'Bevolking_8']
}

results = {}
for metric_name, possible_cols in key_metrics.items():
    for col in possible_cols:
        if col in df_recent.columns:
            results[metric_name] = col
            break

print("Found columns:")
for metric, col in results.items():
    print(f"  {metric}: {col}")

print("\n" + "="*80 + "\n")

# Display year-by-year data
print("YEAR-BY-YEAR BREAKDOWN (2010-2025)")
print("="*80 + "\n")

# Create summary table
summary_data = []
for _, row in df_recent.iterrows():
    year_data = {'Year': int(row['Year'])}

    for metric_name, col in results.items():
        if pd.notna(row[col]):
            year_data[metric_name] = int(row[col])
        else:
            year_data[metric_name] = None

    summary_data.append(year_data)

summary_df = pd.DataFrame(summary_data)

# Display the table
print(summary_df.to_string(index=False))

print("\n" + "="*80 + "\n")

# Calculate natural increase and net migration
if 'Live Births' in summary_df.columns and 'Deaths' in summary_df.columns:
    summary_df['Natural Increase'] = summary_df['Live Births'] - summary_df['Deaths']

if 'Immigration' in summary_df.columns and 'Emigration' in summary_df.columns:
    summary_df['Net Migration'] = summary_df['Immigration'] - summary_df['Emigration']

if 'Natural Increase' in summary_df.columns or 'Net Migration' in summary_df.columns:
    print("CALCULATED METRICS")
    print("="*80 + "\n")

    display_cols = ['Year']
    if 'Natural Increase' in summary_df.columns:
        display_cols.append('Natural Increase')
    if 'Net Migration' in summary_df.columns:
        display_cols.append('Net Migration')

    print(summary_df[display_cols].to_string(index=False))

print("\n" + "="*80 + "\n")

# Summary statistics
print("SUMMARY STATISTICS (2010-2025)")
print("="*80 + "\n")

for metric in ['Live Births', 'Deaths', 'Natural Increase', 'Immigration', 'Emigration', 'Net Migration', 'Population (Jan 1)']:
    if metric in summary_df.columns:
        col_data = summary_df[metric].dropna()
        if len(col_data) > 0:
            print(f"\n{metric}:")
            print(f"  Average: {col_data.mean():,.0f}")
            print(f"  Minimum: {col_data.min():,.0f} ({summary_df.loc[col_data.idxmin(), 'Year']})")
            print(f"  Maximum: {col_data.max():,.0f} ({summary_df.loc[col_data.idxmax(), 'Year']})")

            # Trend
            if len(col_data) >= 2:
                first_val = col_data.iloc[0]
                last_val = col_data.iloc[-1]
                change = last_val - first_val
                pct_change = (change / first_val) * 100 if first_val != 0 else 0
                print(f"  Change 2010→2025: {change:+,.0f} ({pct_change:+.1f}%)")

print("\n" + "="*80 + "\n")

# Key findings
print("KEY FINDINGS")
print("="*80 + "\n")

if 'Natural Increase' in summary_df.columns:
    ni_data = summary_df[['Year', 'Natural Increase']].dropna()
    negative_years = ni_data[ni_data['Natural Increase'] < 0]

    if len(negative_years) > 0:
        print(f"⚠ NATURAL POPULATION DECLINE detected in {len(negative_years)} year(s):")
        for _, row in negative_years.iterrows():
            print(f"  {int(row['Year'])}: {int(row['Natural Increase']):,} (deaths exceeded births)")
    else:
        print("✓ Natural increase positive in all years (births exceed deaths)")

print()

if 'Net Migration' in summary_df.columns and 'Natural Increase' in summary_df.columns:
    latest = summary_df.iloc[-1]
    if pd.notna(latest['Net Migration']) and pd.notna(latest['Natural Increase']):
        print(f"\nLatest year ({int(latest['Year'])}):")
        print(f"  Natural Increase: {int(latest['Natural Increase']):,}")
        print(f"  Net Migration: {int(latest['Net Migration']):,}")

        total_growth = latest['Natural Increase'] + latest['Net Migration']
        print(f"  Total Population Growth: {int(total_growth):,}")

        if latest['Net Migration'] > latest['Natural Increase']:
            pct_migration = (latest['Net Migration'] / total_growth) * 100
            print(f"\n  → Migration accounts for {pct_migration:.1f}% of population growth")
