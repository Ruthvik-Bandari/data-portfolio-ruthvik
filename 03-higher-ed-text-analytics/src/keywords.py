"""Keyword extraction using KeyBERT."""

from __future__ import annotations

import polars as pl
from keybert import KeyBERT
from rich.console import Console

from src.config import PROCESSED_DIR

console = Console()


def extract_keywords(top_n: int = 10) -> pl.DataFrame:
    """Extract keywords from each document using KeyBERT.

    Args:
        top_n: Number of keywords per document.

    Returns:
        DataFrame with keywords column added.
    """
    # Load the latest processed data
    path = PROCESSED_DIR / "with_sentiment.parquet"
    if not path.exists():
        path = PROCESSED_DIR / "topics_assigned.parquet"

    df = pl.read_parquet(path)
    docs = df["clean_text"].to_list()

    console.print(f"Extracting keywords from {len(docs)} documents...")

    kw_model = KeyBERT("all-MiniLM-L6-v2")

    all_keywords: list[str] = []
    for i, doc in enumerate(docs):
        kws = kw_model.extract_keywords(doc, top_n=top_n, stop_words="english")
        keywords_str = "; ".join([kw for kw, _ in kws])
        all_keywords.append(keywords_str)

        if (i + 1) % 100 == 0:
            console.print(f"  {i + 1}/{len(docs)} documents processed")

    df = df.with_columns(pl.Series("keywords", all_keywords))
    df.write_parquet(PROCESSED_DIR / "with_keywords.parquet")
    console.print(f"[green]Keywords extracted. Saved to {PROCESSED_DIR}[/green]")

    return df


if __name__ == "__main__":
    console.print("[bold]Keyword Extraction[/bold]\n")
    extract_keywords()
