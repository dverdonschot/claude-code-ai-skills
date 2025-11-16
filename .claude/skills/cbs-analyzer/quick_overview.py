#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pandas>=2.0.0", "pyarrow>=10.0.0"]
# ///

import pandas as pd

df = pd.read_parquet("data/85524NED/data.parquet")

# Extract year
df['Year'] = df['Perioden'].str[:4].astype(int)

# Filter 2010-2025
df_recent = df[df['Year'].between(2010, 2025)].sort_values('Year')

print("NETHERLANDS POPULATION DEVELOPMENT: 2010-2025")
print("="*80)
print("\nDataset: Bevolking, huishoudens en bevolkingsontwikkeling; vanaf 1899")
print(f"Data for {len(df_recent)} years\n")
print("="*80)
print()

# Key columns (values are in thousands, x 1,000)
cols = {
    'Population': 'MannenEnVrouwen_1',
    'Live Births': 'LevendGeborenKinderen_73',
    'Deaths': 'Overledenen_74',
    'Birth Surplus': 'Geboorteoverschot_75',
    'Immigration': 'Immigratie_76',
    'Emigration': 'EmigratieInclusiefAdministratieveC_77',
    'Migration Balance': 'MigratiesaldoInclusiefAdministrati_78'
}

# Build table
for _, row in df_recent.iterrows():
    year = int(row['Year'])
    pop = int(row[cols['Population']])
    births = int(row[cols['Live Births']])
    deaths = int(row[cols['Deaths']])
    birth_surplus = int(row[cols['Birth Surplus']])
    imm = int(row[cols['Immigration']])
    em = int(row[cols['Emigration']])
    mig_bal = int(row[cols['Migration Balance']])

    print(f"{year}:")
    print(f"  Population (Jan 1):  {pop:>7,} thousand")
    print(f"  Live Births:         {births:>7,} thousand")
    print(f"  Deaths:              {deaths:>7,} thousand")
    print(f"  Natural Increase:    {birth_surplus:>7,} thousand")
    print(f"  Immigration:         {imm:>7,} thousand")
    print(f"  Emigration:          {em:>7,} thousand")
    print(f"  Net Migration:       {mig_bal:>7,} thousand")
    print()

print("="*80)
print("SUMMARY STATISTICS")
print("="*80)
print()

# Calculate averages
births_avg = df_recent[cols['Live Births']].mean()
deaths_avg = df_recent[cols['Deaths']].mean()
natural_avg = df_recent[cols['Birth Surplus']].mean()
mig_avg = df_recent[cols['Migration Balance']].mean()

print(f"Average per year (2010-2025):")
print(f"  Live Births:      {births_avg:>7,.0f} thousand")
print(f"  Deaths:           {deaths_avg:>7,.0f} thousand")
print(f"  Natural Increase: {natural_avg:>7,.0f} thousand")
print(f"  Net Migration:    {mig_avg:>7,.0f} thousand")
print()

# Find extremes
max_births_year = df_recent.loc[df_recent[cols['Live Births']].idxmax(), 'Year']
max_births = df_recent[cols['Live Births']].max()

max_deaths_year = df_recent.loc[df_recent[cols['Deaths']].idxmax(), 'Year']
max_deaths = df_recent[cols['Deaths']].max()

min_natural_year = df_recent.loc[df_recent[cols['Birth Surplus']].idxmin(), 'Year']
min_natural = df_recent[cols['Birth Surplus']].min()

print("\nExtremes:")
print(f"  Highest births:   {max_births:.0f} thousand ({int(max_births_year)})")
print(f"  Highest deaths:   {max_deaths:.0f} thousand ({int(max_deaths_year)})")
print(f"  Lowest natural increase: {min_natural:.0f} thousand ({int(min_natural_year)})")
print()

# Check for negative natural increase
negative_years = df_recent[df_recent[cols['Birth Surplus']] < 0]
if len(negative_years) > 0:
    print(f"⚠️  NATURAL POPULATION DECLINE in {len(negative_years)} year(s):")
    for _, row in negative_years.iterrows():
        print(f"  {int(row['Year'])}: {int(row[cols['Birth Surplus']]):,} thousand")
else:
    print("✓ Natural increase positive in all years")

print()
print("="*80)
