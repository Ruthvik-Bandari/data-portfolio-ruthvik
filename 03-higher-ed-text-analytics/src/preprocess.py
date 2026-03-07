"""Text preprocessing module for higher ed abstracts."""

from __future__ import annotations

import re

import polars as pl
from rich.console import Console

from src.config import EXTRACTED_DIR, PROCESSED_DIR

console = Console()


def clean_text(text: str) -> str:
    """Clean a single text document.

    Args:
        text: Raw abstract text.

    Returns:
        Cleaned text.
    """
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s.,;:!?'-]", "", text)
    return text.strip()


def preprocess_corpus(df: pl.DataFrame) -> pl.DataFrame:
    """Preprocess the entire corpus.

    Args:
        df: DataFrame with 'abstract' column.

    Returns:
        DataFrame with cleaned 'clean_text' column.
    """
    df = df.filter(pl.col("abstract").is_not_null() & (pl.col("abstract").str.len_chars() > 50))
    df = df.with_columns(
        pl.col("abstract").map_elements(clean_text, return_dtype=pl.String).alias("clean_text")
    )
    df = df.filter(pl.col("clean_text").str.len_chars() > 50)
    return df


if __name__ == "__main__":
    console.print("[bold]Text Preprocessing[/bold]\n")

    df = pl.read_parquet(EXTRACTED_DIR / "eric_abstracts.parquet")
    console.print(f"Loaded: {df.height} documents")

    df = preprocess_corpus(df)
    console.print(f"After cleaning: {df.height} documents")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.write_parquet(PROCESSED_DIR / "preprocessed.parquet")
    console.print(f"[green]Saved to {PROCESSED_DIR / 'preprocessed.parquet'}[/green]")
