#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pandas>=2.0.0", "pyarrow>=10.0.0"]
# ///

import pandas as pd
import json
from pathlib import Path

dataset_id = "70703ned"
base_dir = Path("/var/home/ewt/ai-skills/.claude/skills/cbs-analyzer")
df = pd.read_parquet(base_dir / "data" / dataset_id / "data.parquet")

# Load metadata
with open(base_dir / "data" / dataset_id / "metadata.json") as f:
    metadata = json.load(f)

print(f"Dataset: {metadata['title']}")
print(f"Loaded: {len(df):,} rows with {len(df.columns)} columns")
print(f"\nColumns: {df.columns.tolist()}")
print("\n" + "="*80 + "\n")

# Sample data
print("Sample data:")
print(df.head(20))
print("\n" + "="*80 + "\n")

# Check unique periods
print("Period types:")
print(df['Perioden'].value_counts().head(20))
print("\n" + "="*80 + "\n")

# Extract year from period key
# Format: YYYYMMDD for daily, YYYYJJ00 for yearly, YYYYMM## for monthly
df['PeriodKey'] = df['Perioden'].astype(str)
df['Year'] = df['PeriodKey'].str[:4].astype(int)

# Identify record type based on period format
def identify_period_type(period):
    period_str = str(period)
    if period_str.endswith('JJ00'):
        return 'yearly'
    elif period_str.endswith('MM01') or period_str.endswith('MM02') or 'MM' in period_str[4:6]:
        return 'monthly'
    elif len(period_str) == 8 and period_str.isdigit():
        return 'daily'
    else:
        return 'other'

df['PeriodType'] = df['PeriodKey'].apply(identify_period_type)

print("Period type distribution:")
print(df['PeriodType'].value_counts())
print("\n" + "="*80 + "\n")

# Filter for years 2010-2025
df_period = df[df['Year'].between(2010, 2025)].copy()

print(f"Data for 2010-2025: {len(df_period):,} rows")
print(f"Years covered: {sorted(df_period['Year'].unique())}")
print("\n" + "="*80 + "\n")

# Get yearly totals
yearly = df_period[df_period['PeriodType'] == 'yearly'].copy()
yearly = yearly.sort_values('Year')

if len(yearly) > 0:
    print("YEARLY TOTALS (2010-2025)")
    print("="*80)
    print("\nAvailable yearly data columns:")
    numeric_cols = yearly.select_dtypes(include=['float64', 'int64']).columns.tolist()
    print(numeric_cols)
    print()

    # Display key metrics if available
    for col in numeric_cols[:10]:  # First 10 numeric columns
        if yearly[col].notna().any():
            print(f"\n{col}:")
            for _, row in yearly.iterrows():
                if pd.notna(row[col]):
                    print(f"  {row['Year']}: {row[col]:,.0f}")

print("\n" + "="*80 + "\n")

# Get monthly totals for recent years
monthly = df_period[df_period['PeriodType'] == 'monthly'].copy()
monthly = monthly.sort_values(['Year', 'PeriodKey'])

if len(monthly) > 0:
    print(f"MONTHLY DATA: {len(monthly)} monthly records")
    print("\nSample monthly data:")
    print(monthly[['Year', 'Perioden'] + numeric_cols[:5]].head(24))

print("\n" + "="*80 + "\n")

# Analyze daily data if available
daily = df_period[df_period['PeriodType'] == 'daily'].copy()

if len(daily) > 0:
    print(f"DAILY DATA: {len(daily):,} daily records")

    # Parse dates from YYYYMMDD format
    daily['Date'] = pd.to_datetime(daily['PeriodKey'], format='%Y%m%d')
    daily = daily.sort_values('Date')

    print(f"Date range: {daily['Date'].min()} to {daily['Date'].max()}")
    print("\nSample daily data:")
    print(daily[['Date'] + numeric_cols[:5]].head(10))

    # Aggregate by year for daily data
    print("\n" + "="*80)
    print("YEARLY AGGREGATIONS FROM DAILY DATA")
    print("="*80 + "\n")

    yearly_agg = daily.groupby('Year')[numeric_cols].sum()
    yearly_agg = yearly_agg.reset_index()

    for col in numeric_cols[:10]:
        if yearly_agg[col].notna().any() and yearly_agg[col].sum() > 0:
            print(f"\n{col}:")
            for _, row in yearly_agg.iterrows():
                if pd.notna(row[col]) and row[col] > 0:
                    print(f"  {int(row['Year'])}: {row[col]:,.0f}")

print("\n" + "="*80 + "\n")
print("SUMMARY STATISTICS")
print("="*80 + "\n")

# Calculate averages and trends
if len(yearly_agg) > 0:
    for col in numeric_cols[:10]:
        if yearly_agg[col].notna().any() and yearly_agg[col].sum() > 0:
            recent = yearly_agg[yearly_agg['Year'] >= 2020][col]
            earlier = yearly_agg[yearly_agg['Year'] < 2020][col]

            if len(recent) > 0 and len(earlier) > 0:
                avg_recent = recent.mean()
                avg_earlier = earlier.mean()
                change = ((avg_recent - avg_earlier) / avg_earlier) * 100

                print(f"\n{col}:")
                print(f"  Average 2010-2019: {avg_earlier:,.0f}")
                print(f"  Average 2020-2025: {avg_recent:,.0f}")
                print(f"  Change: {change:+.1f}%")
