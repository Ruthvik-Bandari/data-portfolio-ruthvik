"""Visualization module for College Scorecard analytics."""

from __future__ import annotations

from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import polars as pl
from rich.console import Console

from src.config import (
    COLORWAY,
    FEATURES_DIR,
    PORTFOLIO_COLORS,
    REPORTS_DIR,
    REPORTS_IMAGES_DIR,
    TARGET,
)

console = Console()

# Portfolio theme
pio.templates.default = "plotly_white"

CONTROL_LABELS = {1: "Public", 2: "Private Nonprofit", 3: "Private For-Profit"}
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


def plot_earnings_by_sector(df: pl.DataFrame) -> go.Figure:
    """Box plot of median earnings by institution sector."""
    if "CONTROL" not in df.columns:
        return go.Figure()

    data = df.filter(
        pl.col(TARGET).is_not_null() & pl.col("CONTROL").is_in([1, 2, 3])
    ).with_columns(pl.col("CONTROL").cast(pl.Int64).replace_strict(CONTROL_LABELS).alias("Sector"))

    fig = px.box(
        data.to_pandas(),
        x="Sector",
        y=TARGET,
        color="Sector",
        color_discrete_sequence=COLORWAY,
        labels={TARGET: "Median Earnings 10yr Post-Enrollment ($)"},
    )
    fig.update_layout(
        title=dict(
            text=(
                "Median Earnings by Institution Sector<br>"
                f"<sub>Source: College Scorecard | N = {data.height:,} institutions</sub>"
            )
        ),
        yaxis_tickprefix="$",
        yaxis_tickformat=",",
        showlegend=False,
        **_COMMON,
    )
    return fig


def plot_cost_vs_earnings(df: pl.DataFrame) -> go.Figure:
    """Scatter: net price vs median earnings, colored by sector."""
    cost_col = "COSTT4_A" if "COSTT4_A" in df.columns else None
    if cost_col is None or TARGET not in df.columns:
        return go.Figure()

    data = df.filter(
        pl.col(TARGET).is_not_null()
        & pl.col(cost_col).is_not_null()
        & pl.col("CONTROL").is_in([1, 2, 3])
    ).with_columns(pl.col("CONTROL").cast(pl.Int64).replace_strict(CONTROL_LABELS).alias("Sector"))

    fig = px.scatter(
        data.to_pandas(),
        x=cost_col,
        y=TARGET,
        color="Sector",
        hover_data=["INSTNM"] if "INSTNM" in data.columns else None,
        opacity=0.6,
        color_discrete_sequence=COLORWAY,
        labels={cost_col: "Average Cost of Attendance ($)", TARGET: "Median Earnings 10yr ($)"},
    )
    fig.update_layout(
        title=dict(
            text=(
                "Cost of Attendance vs Post-Graduation Earnings<br>"
                f"<sub>N = {data.height:,} institutions | Hover for institution names</sub>"
            )
        ),
        xaxis_tickprefix="$",
        xaxis_tickformat=",",
        yaxis_tickprefix="$",
        yaxis_tickformat=",",
        legend=_LEGEND,
        **_COMMON,
    )
    return fig


def plot_admissions_vs_earnings(df: pl.DataFrame) -> go.Figure:
    """Scatter: admission rate vs earnings."""
    if "ADM_RATE" not in df.columns or TARGET not in df.columns:
        return go.Figure()

    data = df.filter(
        pl.col(TARGET).is_not_null()
        & pl.col("ADM_RATE").is_not_null()
        & pl.col("CONTROL").is_in([1, 2, 3])
    ).with_columns(
        pl.col("CONTROL").cast(pl.Int64).replace_strict(CONTROL_LABELS).alias("Sector"),
        (pl.col("ADM_RATE") * 100).alias("Admission Rate (%)"),
    )

    fig = px.scatter(
        data.to_pandas(),
        x="Admission Rate (%)",
        y=TARGET,
        color="Sector",
        hover_data=["INSTNM"] if "INSTNM" in data.columns else None,
        opacity=0.5,
        color_discrete_sequence=COLORWAY,
        labels={TARGET: "Median Earnings 10yr ($)"},
    )
    fig.update_layout(
        title=dict(
            text=(
                "Selectivity vs Post-Graduation Earnings<br>"
                "<sub>Lower admission rate = more selective</sub>"
            )
        ),
        yaxis_tickprefix="$",
        yaxis_tickformat=",",
        legend=_LEGEND,
        **_COMMON,
    )
    return fig


def plot_earnings_map(df: pl.DataFrame) -> go.Figure:
    """Choropleth of median earnings by state."""
    if "STABBR" not in df.columns or TARGET not in df.columns:
        return go.Figure()

    state_earnings = (
        df.filter(pl.col(TARGET).is_not_null())
        .group_by("STABBR")
        .agg(pl.col(TARGET).median().alias("Median Earnings"))
        .filter(pl.col("STABBR").str.len_chars() == 2)
    )

    fig = go.Figure(
        go.Choropleth(
            locations=state_earnings["STABBR"].to_list(),
            z=state_earnings["Median Earnings"].to_list(),
            locationmode="USA-states",
            colorscale=[
                [0, PORTFOLIO_COLORS["light"]],
                [0.5, PORTFOLIO_COLORS["accent"]],
                [1, PORTFOLIO_COLORS["secondary"]],
            ],
            colorbar=dict(title="Median $", tickprefix="$", tickformat=",", thickness=15),
            hovertemplate="<b>%{location}</b><br>Median Earnings: $%{z:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(
            text="Median Post-Graduation Earnings by State<br><sub>Source: College Scorecard</sub>"
        ),
        geo=dict(scope="usa", bgcolor="white"),
        **_COMMON,
    )
    return fig


def generate_all_visualizations() -> list[Path]:
    """Generate all P2 visualizations."""
    all_paths: list[Path] = []

    df = pl.read_parquet(FEATURES_DIR / "scorecard_features.parquet")
    console.print(f"Loaded: {df.height:,} rows x {df.width} cols")

    charts = [
        ("01_earnings_by_sector", plot_earnings_by_sector(df)),
        ("02_cost_vs_earnings", plot_cost_vs_earnings(df)),
        ("03_admissions_vs_earnings", plot_admissions_vs_earnings(df)),
        ("04_earnings_map", plot_earnings_map(df)),
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
    console.print("[bold]College Scorecard Visualizations[/bold]\n")
    paths = generate_all_visualizations()
    console.print(f"\n[green]Generated {len(paths)} files![/green]")
