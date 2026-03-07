"""Visualization module for IPEDS dashboard charts.

Generates interactive Plotly charts and static Seaborn figures
using the portfolio consistent theme.
"""

from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio
import polars as pl

from src.config import PLOTLY_TEMPLATE, PORTFOLIO_COLORS, REPORTS_DIR

portfolio_template = go.layout.Template(**PLOTLY_TEMPLATE)
pio.templates["portfolio"] = portfolio_template
pio.templates.default = "portfolio"


def plot_enrollment_trends(
    df: pl.DataFrame,
    *,
    group_by: str = "sector",
    output_path: Path | None = None,
) -> go.Figure:
    """Multi line chart showing enrollment trends by institution type.

    Args:
        df: Combined IPEDS DataFrame.
        group_by: Column to group lines by.
        output_path: Optional path to save.

    Returns:
        Plotly Figure object.
    """
    raise NotImplementedError


def plot_geographic_distribution(
    df: pl.DataFrame,
    metric: str = "graduation_rate_total",
    year: int | None = None,
    output_path: Path | None = None,
) -> go.Figure:
    """Choropleth map of institutions colored by a metric.

    Args:
        df: Combined IPEDS DataFrame.
        metric: Column for color encoding.
        year: Specific year to filter to.
        output_path: Optional path to save.

    Returns:
        Plotly Figure object.
    """
    raise NotImplementedError


def plot_completion_heatmap(
    df: pl.DataFrame,
    output_path: Path | None = None,
) -> go.Figure:
    """Heatmap of completion rates by program area and institution type.

    Args:
        df: Combined IPEDS DataFrame.
        output_path: Optional path to save.

    Returns:
        Plotly Figure object.
    """
    raise NotImplementedError


def plot_tuition_vs_graduation(
    df: pl.DataFrame,
    year: int | None = None,
    output_path: Path | None = None,
) -> go.Figure:
    """Scatter plot of tuition vs graduation rate.

    Args:
        df: Combined IPEDS DataFrame.
        year: Specific year.
        output_path: Optional path to save.

    Returns:
        Plotly Figure object.
    """
    raise NotImplementedError


def plot_metric_distribution(
    df: pl.DataFrame,
    metric: str,
    *,
    by_group: str | None = None,
    output_path: Path | None = None,
) -> go.Figure:
    """Violin/box plot of a metric distribution.

    Args:
        df: Combined IPEDS DataFrame.
        metric: Column to plot.
        by_group: Optional grouping column.
        output_path: Optional path to save.

    Returns:
        Plotly Figure object.
    """
    raise NotImplementedError


def save_figure(
    fig: go.Figure,
    name: str,
    *,
    formats: list[str] | None = None,
) -> list[Path]:
    """Save a Plotly figure in multiple formats.

    Args:
        fig: Plotly Figure to save.
        name: Base filename.
        formats: List of formats. Defaults to ["html", "png", "svg"].

    Returns:
        List of paths to saved files.
    """
    raise NotImplementedError


def generate_all_visualizations(df: pl.DataFrame) -> list[Path]:
    """Generate all dashboard visualizations.

    Args:
        df: Final combined IPEDS DataFrame.

    Returns:
        List of paths to generated files.
    """
    raise NotImplementedError


if __name__ == "__main__":
    print(f"IPEDS Visualizer: output to {REPORTS_DIR}")
    print(f"Portfolio colors: {PORTFOLIO_COLORS['primary']}")
    print("Not yet implemented -- run after export phase.")
