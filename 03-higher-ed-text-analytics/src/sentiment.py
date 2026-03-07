"""Sentiment analysis on higher ed research abstracts."""

from __future__ import annotations

import polars as pl
from rich.console import Console
from transformers import pipeline

from src.config import PROCESSED_DIR

console = Console()


def run_sentiment_analysis() -> pl.DataFrame:
    """Run sentiment analysis on preprocessed documents.

    Uses a lightweight distilbert sentiment pipeline.

    Returns:
        DataFrame with sentiment scores added.
    """
    df = pl.read_parquet(PROCESSED_DIR / "topics_assigned.parquet")
    docs = df["clean_text"].to_list()

    console.print(f"Running sentiment on {len(docs)} documents...")

    # Use distilbert for speed
    classifier = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        truncation=True,
        max_length=512,
        device=-1,  # CPU
    )

    # Process in batches
    batch_size = 32
    sentiments = []
    for i in range(0, len(docs), batch_size):
        batch = docs[i : i + batch_size]
        results = classifier(batch)
        for r in results:
            score = r["score"] if r["label"] == "POSITIVE" else -r["score"]
            sentiments.append({"sentiment_label": r["label"], "sentiment_score": score})

        if (i // batch_size) % 10 == 0:
            console.print(f"  Processed {min(i + batch_size, len(docs))}/{len(docs)}")

    sent_df = pl.DataFrame(sentiments)
    df = pl.concat([df, sent_df], how="horizontal")

    df.write_parquet(PROCESSED_DIR / "with_sentiment.parquet")
    console.print(f"[green]Sentiment analysis complete. Saved to {PROCESSED_DIR}[/green]")

    # Summary
    pos = df.filter(pl.col("sentiment_label") == "POSITIVE").height
    neg = df.filter(pl.col("sentiment_label") == "NEGATIVE").height
    console.print(f"  Positive: {pos} ({pos / df.height * 100:.1f}%)")
    console.print(f"  Negative: {neg} ({neg / df.height * 100:.1f}%)")

    return df


if __name__ == "__main__":
    console.print("[bold]Sentiment Analysis[/bold]\n")
    run_sentiment_analysis()
