"""Aspect level sentiment classification."""

from __future__ import annotations

import polars as pl
from rich.console import Console
from transformers import pipeline

from src.config import PROCESSED_DIR

console = Console()


def run_sentiment_analysis() -> pl.DataFrame:
    """Run sentiment analysis on review texts.

    Args: None (reads from processed data).

    Returns:
        DataFrame with sentiment columns added.
    """
    df = pl.read_parquet(PROCESSED_DIR / "with_aspects.parquet")
    texts = df["review_text"].to_list()

    console.print(f"Running sentiment on {len(texts)} reviews...")

    classifier = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        truncation=True,
        max_length=512,
        device=-1,
    )

    labels = []
    scores = []
    batch_size = 64

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        results = classifier(batch)
        for r in results:
            labels.append(r["label"])
            score = r["score"] if r["label"] == "POSITIVE" else -r["score"]
            scores.append(score)

        if (i // batch_size) % 5 == 0:
            console.print(f"  Processed {min(i + batch_size, len(texts))}/{len(texts)}")

    df = df.with_columns(
        pl.Series("sentiment_label", labels),
        pl.Series("sentiment_score", scores),
    )

    df.write_parquet(PROCESSED_DIR / "with_sentiment.parquet")

    pos = df.filter(pl.col("sentiment_label") == "POSITIVE").height
    console.print(f"\n  Positive: {pos} ({pos / df.height * 100:.1f}%)")
    console.print(f"  Negative: {df.height - pos} ({(df.height - pos) / df.height * 100:.1f}%)")
    console.print(f"[green]Saved to {PROCESSED_DIR / 'with_sentiment.parquet'}[/green]")

    return df


if __name__ == "__main__":
    console.print("[bold]Sentiment Analysis[/bold]\n")
    run_sentiment_analysis()
