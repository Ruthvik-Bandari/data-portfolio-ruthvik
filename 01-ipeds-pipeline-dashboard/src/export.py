"""Data export module for IPEDS pipeline outputs.

Exports combined datasets in Parquet, CSV, and BI tool
optimized formats.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
import polars.selectors as cs
from rich.console import Console

from src.config import PROCESSED_DIR, SURVEY_COMPONENTS

console = Console()


def export_parquet(
    df: pl.DataFrame,
    name: str,
    output_dir: Path | None = None,
    *,
    compression: str = "zstd",
) -> Path:
    """Export DataFrame to Parquet format.

    Args:
        df: DataFrame to export.
        name: Base filename (without extension).
        output_dir: Output directory. Defaults to processed/.
        compression: Compression algorithm.

    Returns:
        Path to the exported file.
    """
    out_dir = output_dir or PROCESSED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.parquet"
    df.write_parquet(path, compression=compression)
    return path


def export_csv(
    df: pl.DataFrame,
    name: str,
    output_dir: Path | None = None,
) -> Path:
    """Export DataFrame to CSV format.

    Args:
        df: DataFrame to export.
        name: Base filename (without extension).
        output_dir: Output directory. Defaults to processed/.

    Returns:
        Path to the exported file.
    """
    out_dir = output_dir or PROCESSED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.csv"
    df.write_csv(path)
    return path


def export_for_tableau(
    df: pl.DataFrame,
    name: str,
    output_dir: Path | None = None,
) -> Path:
    """Export DataFrame optimized for Tableau ingestion.

    Fills null strings with "Unknown" and ensures clean headers.

    Args:
        df: DataFrame to export.
        name: Base filename (without extension).
        output_dir: Output directory. Defaults to processed/.

    Returns:
        Path to the exported file.
    """
    out_dir = output_dir or PROCESSED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    clean = df.with_columns(cs.string().fill_null("Unknown"))
    # Lowercase column headers for Tableau
    rename_map = {c: c.lower() for c in clean.columns}
    clean = clean.rename(rename_map)

    path = out_dir / f"{name}_tableau.csv"
    clean.write_csv(path)
    return path


def export_all(
    combined: dict[str, pl.DataFrame],
) -> dict[str, dict[str, Path]]:
    """Export all combined datasets in multiple formats.

    Args:
        combined: Dictionary mapping component to combined DataFrame.

    Returns:
        Nested dict: component -> format -> path.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    result: dict[str, dict[str, Path]] = {}

    for component, df in combined.items():
        label = SURVEY_COMPONENTS.get(component, component)
        console.print(f"\n[bold blue]Exporting {label} ({component.upper()})[/bold blue]")

        name = f"ipeds_{component}"
        paths: dict[str, Path] = {}

        paths["parquet"] = export_parquet(df, name)
        console.print(f"  Parquet: {paths['parquet'].name}")

        paths["csv"] = export_csv(df, name)
        console.print(f"  CSV: {paths['csv'].name}")

        paths["tableau"] = export_for_tableau(df, name)
        console.print(f"  Tableau: {paths['tableau'].name}")

        result[component] = paths

    return result


if __name__ == "__main__":
    from src.clean import clean_all
    from src.combine import combine_all
    from src.harmonize import harmonize_all
    from src.ingest import ingest_all

    console.print("[bold]IPEDS Data Export[/bold]\n")

    raw = ingest_all()
    harmonized = harmonize_all(raw)
    cleaned = clean_all(harmonized)
    combined = combine_all(cleaned)

    console.print("\n[bold]Exporting...[/bold]")
    exports = export_all(combined)

    console.print("\n[bold]Export Summary:[/bold]")
    for component, paths in exports.items():
        label = SURVEY_COMPONENTS.get(component, component)
        for fmt, path in paths.items():
            size_mb = round(path.stat().st_size / (1024 * 1024), 1)
            console.print(f"  {label} [{fmt}]: {size_mb} MB")

    console.print("\n[bold green]Export complete![/bold green]")
