"""Visualization module for course sentiment analytics."""

from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
import polars as pl
from rich.console import Console

from src.config import AGGREGATED_DIR, COLORWAY, PORTFOLIO_COLORS, REPORTS_DIR, REPORTS_IMAGES_DIR

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


def plot_dept_sentiment(dept: pl.DataFrame) -> go.Figure:
    """Horizontal bar: average sentiment by department."""
    dept = dept.sort("avg_sentiment")

    colors = [
        PORTFOLIO_COLORS["danger"] if v < 0 else PORTFOLIO_COLORS["success"]
        for v in dept["avg_sentiment"].to_list()
    ]

    fig = go.Figure(
        go.Bar(
            x=dept["avg_sentiment"].to_list(),
            y=dept["department"].to_list(),
            orientation="h",
            marker_color=colors,
            text=[f"{v:.2f}" for v in dept["avg_sentiment"].to_list()],
            textposition="outside",
            hovertemplate="%{y}<br>Sentiment: %{x:.3f}<br>Reviews: %{customdata}<extra></extra>",
            customdata=dept["review_count"].to_list(),
        )
    )

    fig.update_layout(
        title=dict(
            text=(
                "Average Sentiment Score by Department<br>"
                f"<sub>{dept.height} departments | Green = positive, Red = negative</sub>"
            )
        ),
        xaxis=dict(title="Average Sentiment Score"),
        yaxis=dict(title=""),
        **_COMMON,
    )
    return fig


def plot_aspect_heatmap(dept_aspect: pl.DataFrame) -> go.Figure:
    """Heatmap: departments x aspects colored by sentiment."""
    pivot = dept_aspect.pivot(on="aspect", index="department", values="avg_sentiment")
    depts = pivot["department"].to_list()
    aspects = [c for c in pivot.columns if c != "department"]
    z = pivot.select(aspects).fill_null(0).to_numpy()

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=[a.replace("_", " ").title() for a in aspects],
            y=depts,
            colorscale=[
                [0, PORTFOLIO_COLORS["danger"]],
                [0.5, "white"],
                [1, PORTFOLIO_COLORS["success"]],
            ],
            zmid=0,
            hovertemplate="Dept: %{y}<br>Aspect: %{x}<br>Sentiment: %{z:.3f}<extra></extra>",
            colorbar=dict(title="Sentiment", thickness=15),
        )
    )

    fig.update_layout(
        title=dict(
            text=(
                "Sentiment Heatmap: Department x Aspect<br>"
                "<sub>Red = negative sentiment, Green = positive</sub>"
            )
        ),
        xaxis=dict(title="Aspect Category"),
        yaxis=dict(title=""),
        **_COMMON,
    )
    return fig


def plot_temporal_trends(temporal: pl.DataFrame) -> go.Figure:
    """Line chart: sentiment over time."""
    temporal = temporal.sort(["year", "semester"])
    temporal = temporal.with_columns(
        (pl.col("year").cast(pl.String) + " " + pl.col("semester")).alias("period")
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=temporal["period"].to_list(),
            y=temporal["avg_sentiment"].to_list(),
            mode="lines+markers",
            name="Sentiment",
            line=dict(width=3, color=COLORWAY[0]),
            marker=dict(size=8),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=temporal["period"].to_list(),
            y=[r / 5 for r in temporal["avg_rating"].to_list()],
            mode="lines+markers",
            name="Rating (normalized)",
            line=dict(width=2, color=COLORWAY[1], dash="dash"),
            marker=dict(size=6),
        )
    )

    fig.update_layout(
        title=dict(
            text=(
                "Sentiment & Rating Trends Over Time<br>"
                "<sub>Sentiment score and normalized star rating by semester</sub>"
            )
        ),
        xaxis=dict(title="Semester"),
        yaxis=dict(title="Score"),
        legend=_LEGEND,
        **_COMMON,
    )
    return fig


def plot_rating_sentiment_alignment(alignment: pl.DataFrame) -> go.Figure:
    """Bar + line: rating vs actual sentiment score."""
    alignment = alignment.sort("rating")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=[f"{r} Stars" for r in alignment["rating"].to_list()],
            y=alignment["avg_sentiment"].to_list(),
            marker_color=COLORWAY[: alignment.height],
            text=[f"{v:.2f}" for v in alignment["avg_sentiment"].to_list()],
            textposition="outside",
            name="Avg Sentiment",
        )
    )

    fig.update_layout(
        title=dict(
            text=(
                "Star Rating vs Sentiment Score Alignment<br>"
                "<sub>Do star ratings match the sentiment of review text?</sub>"
            )
        ),
        xaxis=dict(title="Star Rating"),
        yaxis=dict(title="Average Sentiment Score"),
        showlegend=False,
        **_COMMON,
    )
    return fig


def generate_all_visualizations() -> list[Path]:
    """Generate all P4 visualizations."""
    all_paths: list[Path] = []

    dept = pl.read_parquet(AGGREGATED_DIR / "dept_sentiment.parquet")
    dept_aspect = pl.read_parquet(AGGREGATED_DIR / "dept_aspect_sentiment.parquet")
    temporal = pl.read_parquet(AGGREGATED_DIR / "temporal_trends.parquet")
    alignment = pl.read_parquet(AGGREGATED_DIR / "rating_sentiment_alignment.parquet")

    charts = [
        ("01_dept_sentiment", plot_dept_sentiment(dept)),
        ("02_aspect_heatmap", plot_aspect_heatmap(dept_aspect)),
        ("03_temporal_trends", plot_temporal_trends(temporal)),
        ("04_rating_alignment", plot_rating_sentiment_alignment(alignment)),
    ]

    for name, fig in charts:
        if fig.data:
            console.print(f"\n[blue]Generating {name}...[/blue]")
            paths = save_fig(fig, name)
            for p in paths:
                console.print(f"  {p.name}")
            all_paths.extend(paths)

    return all_paths


if __name__ == "__main__":
    console.print("[bold]Course Sentiment Visualizations[/bold]\n")
    paths = generate_all_visualizations()
    console.print(f"\n[green]Generated {len(paths)} files![/green]")
