"""Data ingestion for College Scorecard dataset."""

from __future__ import annotations

from pathlib import Path

import polars as pl
from rich.console import Console

from src.config import NULL_VALUES, PROCESSED_DIR, RAW_DIR

console = Console()


def find_scorecard_csv(raw_dir: Path | None = None) -> Path | None:
    """Find the College Scorecard CSV in the raw directory.

    Args:
        raw_dir: Directory to search. Defaults to config RAW_DIR.

    Returns:
        Path to the CSV file, or None if not found.
    """
    raw = raw_dir or RAW_DIR
    candidates = list(raw.glob("*.csv"))
    if not candidates:
        return None
    # Return the largest CSV (likely the main data file)
    return max(candidates, key=lambda p: p.stat().st_size)


def load_scorecard(raw_dir: Path | None = None) -> pl.DataFrame:
    """Load the College Scorecard CSV into a Polars DataFrame.

    Handles the PrivacySuppressed sentinel values and reads all
    columns as strings initially for safe type inference.

    Args:
        raw_dir: Directory containing the CSV.

    Returns:
        Polars DataFrame with raw scorecard data.
    """
    csv_path = find_scorecard_csv(raw_dir)
    if csv_path is None:
        msg = f"No CSV found in {raw_dir or RAW_DIR}. Download from collegescorecard.ed.gov/data"
        raise FileNotFoundError(msg)

    console.print(f"[bold]Loading {csv_path.name}...[/bold]")
    console.print(f"  File size: {csv_path.stat().st_size / (1024 * 1024):.1f} MB")

    # Read all as string first to handle PrivacySuppressed values
    df = pl.read_csv(
        csv_path,
        null_values=NULL_VALUES,
        infer_schema_length=10000,
        try_parse_dates=True,
    )

    console.print(f"  Loaded: {df.height:,} rows x {df.width:,} columns")
    return df


def profile_nulls(df: pl.DataFrame, threshold: float = 0.5) -> pl.DataFrame:
    """Profile null rates across all columns.

    Args:
        df: DataFrame to profile.
        threshold: Minimum null rate to include in output.

    Returns:
        DataFrame with columns above the threshold, sorted by null rate.
    """
    null_rates = []
    for col in df.columns:
        rate = df[col].null_count() / df.height
        null_rates.append({"column": col, "null_rate": round(rate, 4), "dtype": str(df[col].dtype)})

    result = pl.DataFrame(null_rates).sort("null_rate", descending=True)
    return result.filter(pl.col("null_rate") >= threshold)


if __name__ == "__main__":
    console.print("[bold]College Scorecard Data Ingestion[/bold]\n")

    df = load_scorecard()

    # Profile nulls
    high_null = profile_nulls(df, threshold=0.5)
    console.print(f"\n[yellow]Columns with >50% null: {high_null.height} of {df.width}[/yellow]")

    # Save processed
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "scorecard_raw.parquet"
    df.write_parquet(out_path)
    console.print(f"\n[green]Saved to {out_path}[/green]")
