"""Visualization module for text analytics results."""

from __future__ import annotations

from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from rich.console import Console

from src.config import COLORWAY, PORTFOLIO_COLORS, PROCESSED_DIR, REPORTS_DIR, REPORTS_IMAGES_DIR

console = Console()

_COMMON = dict(title_x=0.5, margin=dict(t=100, b=100, l=80, r=40), font=dict(size=13))
_LEGEND = dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5)


def save_fig(fig: go.Figure, name: str) -> list[Path]:
    """Save figure as HTML and PNG."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    p = REPORTS_DIR / f"{name}.html"
    fig.write_html(str(p), include_plotlyjs="cdn")
    paths.append(p)
    p = REPORTS_IMAGES_DIR / f"{name}.png"
    fig.write_image(str(p), width=1200, height=700, scale=2)
    paths.append(p)
    return paths


def _load_results() -> pl.DataFrame:
    """Load the most complete results file."""
    for name in ["with_keywords.parquet", "with_sentiment.parquet", "topics_assigned.parquet"]:
        path = PROCESSED_DIR / name
        if path.exists():
            return pl.read_parquet(path)
    msg = "No processed results found. Run the pipeline first."
    raise FileNotFoundError(msg)


def plot_topic_distribution(df: pl.DataFrame) -> go.Figure:
    """Bar chart of document counts per topic."""
    topic_counts = (
        df.filter(pl.col("topic") >= 0)
        .group_by("topic")
        .len()
        .sort("len", descending=True)
        .head(15)
    )

    fig = px.bar(
        topic_counts.to_pandas(),
        x="topic",
        y="len",
        color="len",
        color_continuous_scale=[[0, PORTFOLIO_COLORS["accent"]], [1, PORTFOLIO_COLORS["primary"]]],
        labels={"topic": "Topic ID", "len": "Documents"},
        text="len",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        title=dict(
            text=(
                "Document Distribution Across Topics<br>"
                f"<sub>BERTopic modeling on {df.height:,} higher ed research abstracts</sub>"
            )
        ),
        coloraxis_showscale=False,
        xaxis=dict(dtick=1),
        **_COMMON,
    )
    return fig


def plot_sentiment_by_year(df: pl.DataFrame) -> go.Figure:
    """Line chart of average sentiment score by year."""
    if "sentiment_score" not in df.columns or "year" not in df.columns:
        return go.Figure()

    yearly = (
        df.filter(pl.col("year").is_not_null())
        .group_by("year")
        .agg(
            pl.col("sentiment_score").mean().alias("avg_sentiment"),
            pl.len().alias("doc_count"),
        )
        .sort("year")
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=yearly["year"].to_list(),
            y=yearly["avg_sentiment"].to_list(),
            mode="lines+markers+text",
            text=[f"{v:.2f}" for v in yearly["avg_sentiment"].to_list()],
            textposition="top center",
            textfont=dict(size=10),
            line=dict(width=3, color=COLORWAY[0]),
            marker=dict(size=10),
        )
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(
        title=dict(
            text=(
                "Sentiment Trend in Higher Ed Research<br>"
                "<sub>Average sentiment score by publication year (positive = optimistic)</sub>"
            )
        ),
        xaxis=dict(title="Publication Year", dtick=1),
        yaxis=dict(title="Average Sentiment Score"),
        **_COMMON,
    )
    return fig


def plot_topic_by_year_heatmap(df: pl.DataFrame) -> go.Figure:
    """Heatmap of topic prevalence by year."""
    if "topic" not in df.columns or "year" not in df.columns:
        return go.Figure()

    cross = (
        df.filter((pl.col("topic") >= 0) & pl.col("year").is_not_null())
        .group_by(["year", "topic"])
        .len()
        .pivot(on="topic", index="year", values="len")
        .sort("year")
    )

    years = cross["year"].to_list()
    topic_cols = [c for c in cross.columns if c != "year"]
    z = cross.select(topic_cols).fill_null(0).to_numpy()

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=[f"Topic {c}" for c in topic_cols],
            y=[str(y) for y in years],
            colorscale=[[0, PORTFOLIO_COLORS["light"]], [1, PORTFOLIO_COLORS["primary"]]],
            hovertemplate="Year: %{y}<br>%{x}<br>Documents: %{z}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(
            text=(
                "Topic Prevalence Over Time<br>"
                "<sub>Heatmap of document counts per topic per year</sub>"
            )
        ),
        xaxis=dict(title=""),
        yaxis=dict(title="Year"),
        **_COMMON,
    )
    return fig


def plot_sentiment_by_topic(df: pl.DataFrame) -> go.Figure:
    """Bar chart of average sentiment per topic."""
    if "sentiment_score" not in df.columns or "topic" not in df.columns:
        return go.Figure()

    topic_sent = (
        df.filter(pl.col("topic") >= 0)
        .group_by("topic")
        .agg(
            pl.col("sentiment_score").mean().alias("avg_sentiment"),
            pl.len().alias("n"),
        )
        .filter(pl.col("n") >= 5)
        .sort("avg_sentiment")
    )

    colors = [
        PORTFOLIO_COLORS["danger"] if v < 0 else PORTFOLIO_COLORS["success"]
        for v in topic_sent["avg_sentiment"].to_list()
    ]

    fig = go.Figure(
        go.Bar(
            x=topic_sent["avg_sentiment"].to_list(),
            y=[f"Topic {t}" for t in topic_sent["topic"].to_list()],
            orientation="h",
            marker_color=colors,
            text=[f"{v:.2f}" for v in topic_sent["avg_sentiment"].to_list()],
            textposition="outside",
        )
    )
    fig.update_layout(
        title=dict(
            text="Average Sentiment by Topic<br><sub>Red = negative, Green = positive</sub>"
        ),
        xaxis=dict(title="Average Sentiment Score"),
        yaxis=dict(title=""),
        **_COMMON,
    )
    return fig


def generate_all_visualizations() -> list[Path]:
    """Generate all P3 visualizations."""
    all_paths: list[Path] = []
    df = _load_results()
    console.print(f"Loaded: {df.height:,} documents, {df.width} columns")

    charts = [
        ("01_topic_distribution", plot_topic_distribution(df)),
        ("02_sentiment_by_year", plot_sentiment_by_year(df)),
        ("03_topic_year_heatmap", plot_topic_by_year_heatmap(df)),
        ("04_sentiment_by_topic", plot_sentiment_by_topic(df)),
    ]

    for name, fig in charts:
        if fig.data:
            console.print(f"\n[blue]Generating {name}...[/blue]")
            paths = save_fig(fig, name)
            for p in paths:
                console.print(f"  {p.name}")
            all_paths.extend(paths)
        else:
            console.print(f"\n[yellow]Skipped {name}[/yellow]")

    return all_paths


if __name__ == "__main__":
    console.print("[bold]Text Analytics Visualizations[/bold]\n")
    paths = generate_all_visualizations()
    console.print(f"\n[green]Generated {len(paths)} files![/green]")
