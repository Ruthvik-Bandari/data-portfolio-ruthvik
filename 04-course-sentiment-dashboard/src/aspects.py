"""Aspect extraction from course reviews using keyword matching."""

from __future__ import annotations

import polars as pl
from rich.console import Console

from src.config import ASPECT_CATEGORIES, PROCESSED_DIR

console = Console()


def extract_aspects(df: pl.DataFrame) -> pl.DataFrame:
    """Extract aspect mentions from review text.

    Uses keyword matching to identify which aspects each review discusses.

    Args:
        df: DataFrame with review_text column.

    Returns:
        DataFrame with boolean columns for each aspect.
    """
    for aspect, keywords in ASPECT_CATEGORIES.items():
        pattern = "|".join(keywords)
        df = df.with_columns(
            pl.col("review_text").str.to_lowercase().str.contains(pattern).alias(f"has_{aspect}")
        )

    return df


def explode_aspects(df: pl.DataFrame) -> pl.DataFrame:
    """Convert wide aspect columns to long format.

    Each row becomes one review-aspect pair.

    Args:
        df: DataFrame with has_* boolean columns.

    Returns:
        Long format DataFrame with aspect column.
    """
    aspect_cols = [c for c in df.columns if c.startswith("has_")]
    rows = []

    for aspect_col in aspect_cols:
        aspect_name = aspect_col.replace("has_", "")
        subset = df.filter(pl.col(aspect_col)).with_columns(pl.lit(aspect_name).alias("aspect"))
        rows.append(subset)

    if not rows:
        return pl.DataFrame()

    return pl.concat(rows, how="diagonal")


if __name__ == "__main__":
    console.print("[bold]Aspect Extraction[/bold]\n")

    df = pl.read_parquet(PROCESSED_DIR / "reviews.parquet")
    console.print(f"Loaded: {df.height:,} reviews")

    df = extract_aspects(df)

    # Summary
    aspect_cols = [c for c in df.columns if c.startswith("has_")]
    console.print("\nAspect coverage:")
    for col in aspect_cols:
        count = df.filter(pl.col(col)).height
        console.print(
            f"  {col.replace('has_', '')}: {count} reviews ({count / df.height * 100:.1f}%)"
        )

    df.write_parquet(PROCESSED_DIR / "with_aspects.parquet")
    console.print(f"\n[green]Saved to {PROCESSED_DIR / 'with_aspects.parquet'}[/green]")
