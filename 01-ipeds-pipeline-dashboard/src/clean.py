"""Data cleaning module for IPEDS datasets.

Handles deduplication, string column cleaning, and imputation
flag processing on harmonized IPEDS data.
"""

from __future__ import annotations

import polars as pl
from rich.console import Console

from src.config import PRIMARY_KEY, SURVEY_COMPONENTS

console = Console()


def deduplicate_institutions(
    df: pl.DataFrame,
    key_column: str = PRIMARY_KEY,
) -> pl.DataFrame:
    """Remove duplicate institution records.

    Some IPEDS files contain duplicate rows for the same institution
    within a year. Keeps the first occurrence.

    Args:
        df: DataFrame potentially containing duplicates.
        key_column: Column to check for duplicates.

    Returns:
        Deduplicated DataFrame.
    """
    if key_column not in df.columns:
        return df

    before = df.height
    # For components with multiple rows per institution (like Completions),
    # we only deduplicate if UNITID+all other key columns are identical
    df = df.unique(maintain_order=True)
    after = df.height
    if before > after:
        console.print(f"    Removed {before - after} exact duplicate rows")
    return df


def clean_string_columns(df: pl.DataFrame) -> pl.DataFrame:
    """Clean all string columns: strip whitespace.

    Args:
        df: DataFrame with string columns to clean.

    Returns:
        DataFrame with cleaned string columns.
    """
    str_cols = [c for c in df.columns if df[c].dtype == pl.String]
    if not str_cols:
        return df

    strip_exprs = [pl.col(c).str.strip_chars() for c in str_cols]
    return df.with_columns(strip_exprs)


def process_imputation_flags(df: pl.DataFrame) -> pl.DataFrame:
    """Identify and document IPEDS imputation flag columns.

    IPEDS marks imputed values with flag columns starting with 'X'.
    This function keeps them as-is but ensures they're String type
    for consistency.

    Args:
        df: DataFrame with potential imputation flag columns.

    Returns:
        DataFrame with consistent imputation flag types.
    """
    flag_cols = [c for c in df.columns if c.startswith("X")]
    if not flag_cols:
        return df

    cast_exprs = [
        pl.col(c).cast(pl.String, strict=False) for c in flag_cols if df[c].dtype != pl.String
    ]
    if cast_exprs:
        return df.with_columns(cast_exprs)
    return df


def clean_dataframe(df: pl.DataFrame, component: str) -> pl.DataFrame:
    """Apply all cleaning steps to a harmonized DataFrame.

    Orchestrates deduplication, string cleaning, and imputation
    flag processing.

    Args:
        df: Harmonized DataFrame for a single component and year.
        component: Survey component prefix for logging.

    Returns:
        Fully cleaned DataFrame.
    """
    df = deduplicate_institutions(df)
    df = clean_string_columns(df)
    df = process_imputation_flags(df)
    return df


def clean_all(
    data: dict[str, dict[int, pl.DataFrame]],
) -> dict[str, dict[int, pl.DataFrame]]:
    """Clean all harmonized data.

    Args:
        data: Nested dictionary from harmonize_all.

    Returns:
        Same structure with cleaned DataFrames.
    """
    result: dict[str, dict[int, pl.DataFrame]] = {}
    for component, years_data in data.items():
        label = SURVEY_COMPONENTS.get(component, component)
        console.print(f"\n[bold blue]Cleaning {label} ({component.upper()})[/bold blue]")
        result[component] = {}
        for year, df in sorted(years_data.items()):
            cleaned = clean_dataframe(df, component)
            result[component][year] = cleaned
            console.print(f"  {year}: {cleaned.height:,} rows x {cleaned.width} cols")
    return result


if __name__ == "__main__":
    from src.harmonize import harmonize_all
    from src.ingest import ingest_all

    console.print("[bold]IPEDS Data Cleaning[/bold]\n")

    console.print("[bold]Step 1: Ingesting...[/bold]")
    raw_data = ingest_all()

    console.print("\n[bold]Step 2: Harmonizing...[/bold]")
    harmonized = harmonize_all(raw_data)

    console.print("\n[bold]Step 3: Cleaning...[/bold]")
    cleaned = clean_all(harmonized)

    console.print("\n[bold green]Cleaning complete![/bold green]")
