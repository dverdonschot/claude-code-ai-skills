---
name: cbs-analyzer
description: Download and analyze CBS (Dutch Statistics) Open Data datasets by ID. Use when user asks to analyze CBS datasets, explore energy/population/economic trends in Dutch data, query specific dataset IDs like 83140NED, or wants renewable energy trends, demographic analysis, or other Netherlands statistics.
---

# CBS Dataset Analyzer

Download and analyze CBS Open Data datasets using the opencbs CLI and pandas for data analysis.

## Context

Use this skill when:
- User asks to analyze a CBS dataset by ID (e.g., 83140NED)
- User wants to explore trends or patterns in CBS data
- User requests information about Dutch statistics
- User needs to download and query CBS Open Data

## Process

### 1. Check if Dataset Exists Locally

```bash
# Check if dataset is already downloaded
ls -la data/{dataset_id}/ 2>/dev/null
```

If `data.parquet` exists, skip to step 3.

### 2. Download Dataset (if needed)

```bash
# Get dataset information
./.claude/skills/cbs-analyzer/scripts/cli.py info {dataset_id}

# Check row count
./.claude/skills/cbs-analyzer/scripts/cli.py data {dataset_id} --count

# Download and save (adjust limit based on size)
./.claude/skills/cbs-analyzer/scripts/cli.py save {dataset_id} --limit 10000
```

**Important**: For datasets >10k rows, ask user about appropriate limit.

### 3. Explore Dimensions

```bash
# List available entity sets to see dimension names
./.claude/skills/cbs-analyzer/scripts/cli.py entities {dataset_id}

# View specific dimensions (e.g., energy carriers, time periods)
./.claude/skills/cbs-analyzer/scripts/cli.py dimension {dataset_id} Energiedragers
./.claude/skills/cbs-analyzer/scripts/cli.py dimension {dataset_id} Perioden --limit 100
```

### 4. Analyze Data with Python

Use the CLI's inline script with pandas (it has all dependencies):

```bash
./.claude/skills/cbs-analyzer/scripts/client.py
```

Or create a Python analysis script using uv:

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = ["pandas>=2.0.0", "matplotlib>=3.0.0"]
# ///

import pandas as pd
import json
from pathlib import Path

dataset_id = "83140NED"
df = pd.read_parquet(f"data/{dataset_id}/data.parquet")

# Load metadata
with open(f"data/{dataset_id}/metadata.json") as f:
    metadata = json.load(f)

print(f"Dataset: {metadata['title']}")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# Your analysis here
print(df.head())
print(df.describe())
```

### 5. Answer User Questions

Based on the analysis:
- Filter data according to user's criteria
- Create visualizations if requested
- Aggregate and summarize findings
- Provide clear, concise insights

## Guidelines

### Data Download
- Always check if data exists before downloading
- Use reasonable limits for large datasets (default: 10000 rows)
- Save datasets with metadata for future reference
- Use CLI commands via Bash (uv handles dependencies automatically)

### Analysis Approach
- Start with dataset overview (shape, columns, sample rows)
- Understand dimensions before filtering
- Pay attention to time period formats (e.g., "2020JJ00" = year 2020)
- Use descriptive statistics to identify patterns
- Create visualizations for trends over time

### Time Period Handling
CBS uses specific formats:
- `2020JJ00` = Year 2020
- `2020KW01` = Quarter 1, 2020
- `2020MM01` = January 2020

Filter accordingly when analyzing time ranges.

### Renewable Energy Categories
When analyzing energy data, renewable sources typically include:
- Wind energy (Windenergie)
- Solar energy (Zonne-energie)
- Biomass (Biomassa)
- Hydroelectric (Waterkracht)
- Geothermal (Geothermische energie)

Check the Energiedragers dimension to identify exact keys.

## Output

Provide:
1. Dataset overview (title, size, time coverage)
2. Relevant dimension information
3. Direct answer to user's question
4. Supporting data/visualizations
5. Key insights and trends
6. Suggestions for further analysis (if applicable)

## Example

**User**: "Analyze CBS dataset 83140NED and show renewable energy trends from 2015-2025"

**Steps**:
1. Check if data/83140NED/data.parquet exists
2. If not: `./.claude/skills/cbs-analyzer/scripts/cli.py save 83140NED --limit 10000`
3. View dimensions: `./.claude/skills/cbs-analyzer/scripts/cli.py dimension 83140NED Energiedragers`
4. View time periods: `./.claude/skills/cbs-analyzer/scripts/cli.py dimension 83140NED Perioden`
5. Load data, filter for renewable sources and 2015-2025
6. Calculate trends, create visualization
7. Explain findings

## Error Handling

- If dataset ID doesn't exist: suggest checking opendata.cbs.nl
- If download fails: check network connectivity
- If data is too large: help user create filters
- If analysis fails: explain issue and suggest alternatives
