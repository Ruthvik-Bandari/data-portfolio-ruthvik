"""Export text analytics results for BI tools."""

from __future__ import annotations

from pathlib import Path

import polars as pl
import polars.selectors as cs
from rich.console import Console

from src.config import PROCESSED_DIR

console = Console()


def export_all() -> dict[str, Path]:
    """Export processed text data for Tableau."""
    for name in ["with_keywords.parquet", "with_sentiment.parquet", "topics_assigned.parquet"]:
        path = PROCESSED_DIR / name
        if path.exists():
            df = pl.read_parquet(path)
            break
    else:
        console.print("[red]No results to export[/red]")
        return {}

    csv_path = PROCESSED_DIR / "text_analytics_tableau.csv"
    clean = df.with_columns(cs.string().fill_null("Unknown"))
    clean.write_csv(csv_path)
    console.print(f"  Tableau CSV: {csv_path.name} ({csv_path.stat().st_size / 1024:.0f} KB)")
    return {"tableau_csv": csv_path}


if __name__ == "__main__":
    console.print("[bold]Text Analytics Export[/bold]\n")
    export_all()
