"""Export module for College Scorecard processed data."""

from __future__ import annotations

from pathlib import Path

import polars as pl
import polars.selectors as cs
from rich.console import Console

from src.config import FEATURES_DIR, PROCESSED_DIR

console = Console()


def export_all() -> dict[str, Path]:
    """Export processed data in multiple formats."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = pl.read_parquet(FEATURES_DIR / "scorecard_features.parquet")
    paths: dict[str, Path] = {}

    # CSV for Tableau
    csv_path = PROCESSED_DIR / "scorecard_tableau.csv"
    clean = df.with_columns(cs.string().fill_null("Unknown"))
    clean.write_csv(csv_path)
    paths["tableau_csv"] = csv_path
    console.print(
        f"  Tableau CSV: {csv_path.name} ({csv_path.stat().st_size / 1024 / 1024:.1f} MB)"
    )

    return paths


if __name__ == "__main__":
    console.print("[bold]College Scorecard Export[/bold]\n")
    paths = export_all()
    console.print(f"\n[green]Exported {len(paths)} files[/green]")
