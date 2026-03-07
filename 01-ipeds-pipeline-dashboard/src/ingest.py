"""Data ingestion module for IPEDS raw CSV files.

Handles reading raw IPEDS CSVs with proper encoding detection,
null value mapping, and metadata extraction.
"""

from __future__ import annotations

import re
from pathlib import Path

import polars as pl
from rich.console import Console
from rich.table import Table

from src.config import (
    COMPONENT_FILE_PATTERNS,
    ENCODING_PRIORITY,
    NULL_VALUES,
    RAW_DIR,
    SURVEY_COMPONENTS,
    SURVEY_YEARS,
)

console = Console()


def read_csv_with_fallback(
    path: Path,
    *,
    null_values: list[str] | None = None,
    infer_schema_length: int = 10000,
) -> pl.DataFrame:
    """Read a CSV file with encoding fallback.

    Attempts UTF-8 first, then falls back through configured encodings.

    Args:
        path: Path to the CSV file.
        null_values: Values to treat as null. Defaults to IPEDS null codes.
        infer_schema_length: Number of rows for schema inference.

    Returns:
        Polars DataFrame with the CSV contents.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If no encoding succeeds.
    """
    if not path.exists():
        msg = f"CSV file not found: {path}"
        raise FileNotFoundError(msg)

    nv = null_values if null_values is not None else NULL_VALUES

    for encoding in ENCODING_PRIORITY:
        try:
            return pl.read_csv(
                path,
                encoding=encoding,
                null_values=nv,
                infer_schema_length=infer_schema_length,
                try_parse_dates=True,
            )
        except Exception:
            continue

    msg = f"Failed to read {path} with any encoding: {ENCODING_PRIORITY}"
    raise ValueError(msg)


def parse_filename(filename: str) -> tuple[str, int] | None:
    """Extract component prefix and year from an IPEDS filename.

    Handles patterns like: hd2018.csv, effy2020.csv, c2021_a.csv, gr2022.csv

    Args:
        filename: The CSV filename (not full path).

    Returns:
        Tuple of (component_prefix, year) or None if not recognized.
    """
    name = filename.lower()
    match = re.match(r"^(hd|effy|gr|c)(\d{4})(?:_a)?\.csv$", name)
    if match:
        return match.group(1), int(match.group(2))
    return None


def discover_raw_files(raw_dir: Path | None = None) -> dict[str, dict[int, Path]]:
    """Discover all raw IPEDS CSV files organized by component and year.

    Args:
        raw_dir: Directory containing raw CSVs. Defaults to config RAW_DIR.

    Returns:
        Nested dictionary: component_prefix -> year -> Path.
    """
    raw = raw_dir or RAW_DIR
    result: dict[str, dict[int, Path]] = {}

    for csv_path in sorted(raw.glob("*.csv")):
        parsed = parse_filename(csv_path.name)
        if parsed is None:
            continue
        component, year = parsed
        if component not in result:
            result[component] = {}
        result[component][year] = csv_path

    return result


def ingest_component(
    component: str,
    years: list[int] | None = None,
    raw_dir: Path | None = None,
) -> dict[int, pl.DataFrame]:
    """Ingest all years of a single IPEDS survey component.

    Args:
        component: Survey component prefix (e.g., "hd", "effy", "c", "gr").
        years: List of years to ingest. Defaults to all configured years.
        raw_dir: Directory containing raw CSVs. Defaults to config RAW_DIR.

    Returns:
        Dictionary mapping year to DataFrame for the given component.
    """
    raw = raw_dir or RAW_DIR
    target_years = years or SURVEY_YEARS
    pattern = COMPONENT_FILE_PATTERNS.get(component)
    if pattern is None:
        msg = f"Unknown component: {component}"
        raise ValueError(msg)

    result: dict[int, pl.DataFrame] = {}
    for year in target_years:
        filename = pattern.format(year=year)
        path = raw / filename
        if not path.exists():
            console.print(f"  [yellow]⚠ Missing: {filename}[/yellow]")
            continue
        df = read_csv_with_fallback(path)
        result[year] = df
        console.print(f"  [green]✓[/green] {filename}: {df.height:,} rows x {df.width} cols")

    return result


def ingest_all(raw_dir: Path | None = None) -> dict[str, dict[int, pl.DataFrame]]:
    """Ingest all survey components across all years.

    Args:
        raw_dir: Directory containing raw CSVs. Defaults to config RAW_DIR.

    Returns:
        Nested dictionary: component -> year -> DataFrame.
    """
    result: dict[str, dict[int, pl.DataFrame]] = {}
    for component, label in SURVEY_COMPONENTS.items():
        console.print(f"\n[bold blue]▶ {label} ({component.upper()})[/bold blue]")
        result[component] = ingest_component(component, raw_dir=raw_dir)
    return result


def get_file_metadata(path: Path) -> dict[str, str | int | float]:
    """Extract metadata from a raw CSV file.

    Args:
        path: Path to the CSV file.

    Returns:
        Dictionary with file metadata.
    """
    df = read_csv_with_fallback(path)
    null_counts = df.null_count().row(0)
    total_nulls = sum(null_counts)
    total_cells = df.height * df.width

    return {
        "filename": path.name,
        "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
        "row_count": df.height,
        "column_count": df.width,
        "total_null_count": total_nulls,
        "null_rate": round(total_nulls / total_cells, 4) if total_cells > 0 else 0.0,
    }


def print_ingest_summary(data: dict[str, dict[int, pl.DataFrame]]) -> None:
    """Print a rich summary table of ingested data.

    Args:
        data: Nested dictionary from ingest_all.
    """
    table = Table(title="IPEDS Ingestion Summary")
    table.add_column("Component", style="bold")
    table.add_column("Years", justify="center")
    table.add_column("Total Rows", justify="right")
    table.add_column("Columns (range)", justify="center")

    for component, years_data in data.items():
        label = SURVEY_COMPONENTS.get(component, component)
        year_range = f"{min(years_data)}-{max(years_data)}" if years_data else "none"
        total_rows = sum(df.height for df in years_data.values())
        col_counts = [df.width for df in years_data.values()]
        col_range = f"{min(col_counts)}-{max(col_counts)}" if col_counts else "0"

        table.add_row(
            label,
            f"{len(years_data)} ({year_range})",
            f"{total_rows:,}",
            col_range,
        )

    console.print()
    console.print(table)


if __name__ == "__main__":
    console.print("[bold]IPEDS Data Ingestion[/bold]")
    console.print(f"Raw directory: {RAW_DIR}")
    console.print(f"Components: {list(SURVEY_COMPONENTS.keys())}")
    console.print(f"Years: {SURVEY_YEARS}")

    discovered = discover_raw_files()
    if not discovered:
        console.print("[red]No IPEDS CSV files found in data/raw/[/red]")
        console.print("See data/README.md for download instructions.")
    else:
        console.print(f"\n[green]Found files for {len(discovered)} components[/green]")
        data = ingest_all()
        print_ingest_summary(data)
