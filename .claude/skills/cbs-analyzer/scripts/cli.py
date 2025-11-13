#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "requests>=2.31.0",
#     "pandas>=2.0.0",
#     "diskcache>=5.6.0",
#     "click>=8.1.0",
#     "rich>=13.0.0",
#     "pyarrow>=14.0.0",
# ]
# ///
"""Command-line interface for OpenCBS"""

import sys
import os
from pathlib import Path
from datetime import datetime
import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import pandas as pd

# Import the CBSClient from client.py in the same directory
from client import CBSClient

console = Console()

# Default data directory
DATA_DIR = Path("./data")


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """OpenCBS - CBS Open Data API Client"""
    pass


@cli.command()
@click.argument('dataset_id')
def info(dataset_id: str):
    """
    Get information about a dataset

    Example: opencbs info 83140NED
    """
    console.print(f"[bold blue]Fetching info for dataset: {dataset_id}[/bold blue]")

    client = CBSClient()
    try:
        dataset_info = client.get_dataset_info(dataset_id)

        console.print(f"\n[bold green]Dataset Information[/bold green]")
        console.print(f"[cyan]Title:[/cyan] {dataset_info.get('Title', 'N/A')}")
        console.print(f"[cyan]Identifier:[/cyan] {dataset_info.get('Identifier', 'N/A')}")
        console.print(f"[cyan]Modified:[/cyan] {dataset_info.get('Modified', 'N/A')}")
        console.print(f"[cyan]Frequency:[/cyan] {dataset_info.get('Frequency', 'N/A')}")
        console.print(f"[cyan]Period:[/cyan] {dataset_info.get('Period', 'N/A')}")
        console.print(f"\n[cyan]Summary:[/cyan]")
        console.print(dataset_info.get('Summary', 'N/A'))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())
        raise click.Abort()


@cli.command()
@click.argument('dataset_id')
def properties(dataset_id: str):
    """
    List all data properties/columns for a dataset

    Example: opencbs properties 83140NED
    """
    console.print(f"[bold blue]Fetching properties for dataset: {dataset_id}[/bold blue]")

    client = CBSClient()
    try:
        props_df = client.get_data_properties(dataset_id)

        table = Table(title=f"Data Properties for {dataset_id}")
        table.add_column("ID", style="cyan")
        table.add_column("Key", style="yellow")
        table.add_column("Title", style="green")
        table.add_column("Unit", style="magenta")
        table.add_column("Type", style="blue")

        for _, row in props_df.iterrows():
            table.add_row(
                str(row['ID']),
                str(row['Key']),
                str(row['Title'])[:50],  # Truncate long titles
                str(row['Unit']) if pd.notna(row['Unit']) else '',
                str(row['Datatype']) if pd.notna(row['Datatype']) else ''
            )

        console.print(table)
        console.print(f"\n[green]Total properties: {len(props_df)}[/green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@cli.command()
@click.argument('dataset_id')
@click.argument('dimension_name')
@click.option('--limit', '-l', default=20, help='Number of rows to display')
def dimension(dataset_id: str, dimension_name: str, limit: int):
    """
    Get dimension values (e.g., Energiedragers, Perioden)

    Example: opencbs dimension 83140NED Energiedragers
    """
    console.print(
        f"[bold blue]Fetching dimension '{dimension_name}' for dataset: {dataset_id}[/bold blue]"
    )

    client = CBSClient()
    try:
        dim_df = client.get_dimensions(dataset_id, dimension_name)

        # Display table
        table = Table(title=f"{dimension_name} Dimension")

        # Add columns dynamically
        for col in dim_df.columns:
            table.add_column(col, style="cyan" if col == "Key" else "white")

        # Add rows (limited)
        for _, row in dim_df.head(limit).iterrows():
            table.add_row(*[str(val)[:60] for val in row.values])

        console.print(table)

        if len(dim_df) > limit:
            console.print(f"\n[yellow]Showing {limit} of {len(dim_df)} rows[/yellow]")
        else:
            console.print(f"\n[green]Total rows: {len(dim_df)}[/green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@cli.command()
@click.argument('dataset_id')
@click.option('--limit', '-l', default=10, help='Number of rows to fetch (default: 10)')
@click.option('--output', '-o', help='Output file (CSV, JSON, or Parquet)')
@click.option('--select', '-s', help='Comma-separated list of columns')
@click.option('--count', '-c', is_flag=True, help='Show total row count only')
@click.option('--auto-save', is_flag=True, help='Auto-save to data/{dataset_id}/data.parquet')
def data(dataset_id: str, limit: int, output: str, select: str, count: bool, auto_save: bool):
    """
    Fetch dataset observations

    Example: opencbs data 83140NED --limit 100 --output data.csv
    Example: opencbs data 83140NED --count  (shows total rows)
    Example: opencbs data 83140NED --limit 1000 --auto-save  (saves to data/{dataset_id}/data.parquet)
    """
    client = CBSClient()
    try:
        # If --count flag, just show the total count
        if count:
            console.print(f"[bold blue]Counting observations in dataset: {dataset_id}[/bold blue]")
            total = client.count_observations(dataset_id)
            console.print(f"\n[green]Total observations: {total:,}[/green]")
            return

        console.print(f"[bold blue]Fetching data from dataset: {dataset_id}[/bold blue]")

        # Get total count first
        total_count = client.count_observations(dataset_id)

        select_cols = select.split(',') if select else None

        df = client.get_data(
            dataset_id,
            select=select_cols,
            top=limit
        )

        console.print(f"\n[green]Fetched {len(df)} of {total_count:,} total rows ({len(df.columns)} columns)[/green]")

        if len(df) < total_count:
            console.print(f"[yellow]💡 Use --limit {total_count} to fetch all rows[/yellow]")

        # Display preview
        console.print("\n[bold]Data Preview:[/bold]")
        console.print(df.head(10).to_string())

        # Auto-save to structured data directory
        if auto_save:
            dataset_dir = DATA_DIR / dataset_id
            dataset_dir.mkdir(parents=True, exist_ok=True)
            output_path = dataset_dir / "data.parquet"
            df.to_parquet(output_path, index=False, engine='pyarrow')
            console.print(f"\n[green]Data auto-saved to: {output_path}[/green]")

        # Save if output specified
        if output:
            # Ensure parent directory exists
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output.endswith('.csv'):
                df.to_csv(output, index=False)
            elif output.endswith('.json'):
                df.to_json(output, orient='records', indent=2)
            elif output.endswith('.parquet'):
                df.to_parquet(output, index=False, engine='pyarrow')
            else:
                console.print("[yellow]Unknown format, saving as Parquet[/yellow]")
                df.to_parquet(output, index=False, engine='pyarrow')

            console.print(f"\n[green]Data saved to: {output}[/green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@cli.command()
@click.argument('dataset_id')
def entities(dataset_id: str):
    """
    List all available entity sets for a dataset

    Example: opencbs entities 83140NED
    """
    console.print(f"[bold blue]Fetching entity sets for dataset: {dataset_id}[/bold blue]")

    client = CBSClient()
    try:
        entity_sets = client.list_entity_sets(dataset_id)

        table = Table(title=f"Entity Sets for {dataset_id}")
        table.add_column("Entity Set Name", style="cyan")

        for entity_set in entity_sets:
            table.add_row(entity_set)

        console.print(table)
        console.print(f"\n[green]Total entity sets: {len(entity_sets)}[/green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@cli.command()
def clear_cache():
    """Clear the API response cache"""
    client = CBSClient()
    client.clear_cache()
    console.print("[green]Cache cleared successfully![/green]")


@cli.command()
@click.argument('dataset_id')
@click.option('--limit', '-l', default=None, type=int, help='Number of rows to fetch (default: all)')
@click.option('--select', '-s', help='Comma-separated list of columns')
def save(dataset_id: str, limit: int, select: str):
    """
    Fetch and save dataset to structured data directory

    Saves to: data/{dataset_id}/data.parquet

    Example: opencbs save 83140NED --limit 10000
    """
    client = CBSClient()
    try:
        console.print(f"[bold blue]Fetching and saving dataset: {dataset_id}[/bold blue]")

        # Get dataset info for metadata
        dataset_info = client.get_dataset_info(dataset_id)
        total_count = client.count_observations(dataset_id)

        # Determine how many rows to fetch
        fetch_limit = limit if limit else total_count

        console.print(f"[cyan]Fetching {fetch_limit:,} of {total_count:,} rows...[/cyan]")

        select_cols = select.split(',') if select else None

        df = client.get_data(
            dataset_id,
            select=select_cols,
            top=fetch_limit
        )

        # Save with metadata
        metadata = {
            'dataset_id': dataset_id,
            'title': dataset_info.get('Title', 'N/A'),
            'fetched_at': datetime.now().isoformat(),
            'total_rows_available': total_count,
            'rows_saved': len(df),
            'columns': list(df.columns)
        }

        saved_path = client.save_dataset(dataset_id, df, metadata=metadata)
        console.print(f"\n[green]✓ Dataset saved to: {saved_path}[/green]")
        console.print(f"[green]✓ Metadata saved to: {saved_path.parent}/metadata.json[/green]")
        console.print(f"\n[cyan]Saved {len(df):,} rows with {len(df.columns)} columns[/cyan]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())
        raise click.Abort()


@cli.command()
@click.argument('dataset_id')
def load(dataset_id: str):
    """
    Load dataset from structured data directory

    Example: opencbs load 83140NED
    """
    client = CBSClient()
    try:
        console.print(f"[bold blue]Loading dataset: {dataset_id}[/bold blue]")

        df = client.load_dataset(dataset_id)

        if df is None:
            console.print(f"[yellow]No saved data found for {dataset_id}[/yellow]")
            console.print(f"[yellow]Use 'opencbs save {dataset_id}' to fetch and save the dataset first[/yellow]")
            return

        console.print(f"\n[green]Loaded {len(df):,} rows with {len(df.columns)} columns[/green]")

        # Check for metadata
        metadata_path = client.data_dir / dataset_id / "metadata.json"
        if metadata_path.exists():
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            console.print(f"\n[cyan]Dataset: {metadata.get('title', 'N/A')}[/cyan]")
            console.print(f"[cyan]Fetched at: {metadata.get('fetched_at', 'N/A')}[/cyan]")

        # Display preview
        console.print("\n[bold]Data Preview:[/bold]")
        console.print(df.head(10).to_string())

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


if __name__ == '__main__':
    cli()
