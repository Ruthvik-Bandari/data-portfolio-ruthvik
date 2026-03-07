"""BERTopic topic modeling pipeline."""

from __future__ import annotations

import polars as pl
from bertopic import BERTopic
from hdbscan import HDBSCAN
from rich.console import Console
from sentence_transformers import SentenceTransformer
from umap import UMAP

from src.config import (
    EMBEDDING_MODEL,
    MIN_CLUSTER_SIZE,
    MIN_TOPIC_SIZE,
    MODELS_DIR,
    N_NEIGHBORS,
    PROCESSED_DIR,
    REPORTS_IMAGES_DIR,
)

console = Console()


def build_topic_model() -> BERTopic:
    """Build a BERTopic model with configured parameters.

    Returns:
        Configured BERTopic instance.
    """
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    umap_model = UMAP(
        n_neighbors=N_NEIGHBORS,
        n_components=5,
        min_dist=0.0,
        metric="cosine",
        random_state=42,
    )
    hdbscan_model = HDBSCAN(
        min_cluster_size=MIN_CLUSTER_SIZE,
        min_samples=5,
        metric="euclidean",
        prediction_data=True,
    )

    return BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        min_topic_size=MIN_TOPIC_SIZE,
        verbose=True,
    )


def run_topic_modeling() -> tuple[BERTopic, pl.DataFrame]:
    """Run the full topic modeling pipeline.

    Returns:
        Tuple of (fitted BERTopic model, DataFrame with topic assignments).
    """
    df = pl.read_parquet(PROCESSED_DIR / "preprocessed.parquet")
    docs = df["clean_text"].to_list()
    console.print(f"Modeling {len(docs)} documents...")

    model = build_topic_model()
    topics, probs = model.fit_transform(docs)

    df = df.with_columns(
        pl.Series("topic", topics),
        pl.Series(
            "topic_prob", [float(p) for p in probs] if probs is not None else [0.0] * len(topics)
        ),
    )

    # Save model
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model.save(
        str(MODELS_DIR / "bertopic_model"),
        serialization="safetensors",
        save_ctfidf=True,
        save_embedding_model=EMBEDDING_MODEL,
    )

    # Save results
    df.write_parquet(PROCESSED_DIR / "topics_assigned.parquet")

    # Topic info
    topic_info = model.get_topic_info()
    console.print(f"\n[green]Found {len(topic_info) - 1} topics (excluding outliers)[/green]")

    # Save visualizations
    REPORTS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    try:
        fig = model.visualize_barchart(top_n_topics=12)
        fig.write_html(str(REPORTS_IMAGES_DIR.parent / "topic_barchart.html"))
        fig.write_image(str(REPORTS_IMAGES_DIR / "topic_barchart.png"), width=1200, height=800)
        console.print("  Saved topic barchart")
    except Exception as e:
        console.print(f"[yellow]Barchart viz failed: {e}[/yellow]")

    try:
        fig = model.visualize_topics()
        fig.write_html(str(REPORTS_IMAGES_DIR.parent / "topic_map.html"))
        console.print("  Saved topic map")
    except Exception as e:
        console.print(f"[yellow]Topic map viz failed: {e}[/yellow]")

    return model, df


if __name__ == "__main__":
    console.print("[bold]BERTopic Topic Modeling[/bold]\n")
    model, df = run_topic_modeling()
    console.print(f"\n[bold green]Topic modeling complete! {df.height} docs assigned.[/bold green]")
