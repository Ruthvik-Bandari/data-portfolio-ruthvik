"""Export course sentiment data for BI tools."""

from __future__ import annotations

import polars as pl
import polars.selectors as cs
from rich.console import Console

from src.config import PROCESSED_DIR

console = Console()


def export_all() -> None:
    """Export processed data as Tableau CSV."""
    df = pl.read_parquet(PROCESSED_DIR / "with_sentiment.parquet")
    csv_path = PROCESSED_DIR / "course_sentiment_tableau.csv"
    clean = df.with_columns(cs.string().fill_null("Unknown"))
    clean.write_csv(csv_path)
    size_mb = csv_path.stat().st_size / 1024 / 1024
    console.print(f"  Tableau CSV: {csv_path.name} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    console.print("[bold]Course Sentiment Export[/bold]\n")
    export_all()
