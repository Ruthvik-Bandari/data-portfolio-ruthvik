"""Visualization module for IPEDS dashboard charts.

Generates interactive Plotly charts from the processed IPEDS data.
All charts use the portfolio consistent theme and are exported as
self contained HTML files and static PNG images.

Key IPEDS columns used:
- HD: UNITID, INSTNM, STABBR, CONTROL, ICLEVEL, INSTSIZE
  CONTROL: 1=Public, 2=Private nonprofit, 3=Private for-profit
- EFFY: UNITID, EFYTOTLT (total enrollment), EFFYLEV (level), LSTUDY
- GR: UNITID, GRTOTLT (total in cohort), GRTYPE, GRTOTLM/GRTOTLW (completers)
  Note: GRTOTLT is cohort SIZE, not graduation rate. Rate must be computed.
- C: UNITID, CTOTALT (total completions), AWLEVEL (award level), MAJORNUM
"""

from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio
import polars as pl
from rich.console import Console

from src.config import (
    COLORWAY,
    PLOTLY_TEMPLATE,
    PORTFOLIO_COLORS,
    PROCESSED_DIR,
    REPORTS_DIR,
    REPORTS_IMAGES_DIR,
)

console = Console()

# ── Register Portfolio Theme ─────────────────────────────────────────────────
portfolio_template = go.layout.Template(**PLOTLY_TEMPLATE)
pio.templates["portfolio"] = portfolio_template
pio.templates.default = "portfolio"

# IPEDS CONTROL codes
CONTROL_LABELS = {1: "Public", 2: "Private Nonprofit", 3: "Private For-Profit"}

# Common layout settings
_COMMON_LAYOUT = dict(
    title_x=0.5,
    title_xanchor="center",
    margin=dict(t=100, b=100, l=80, r=40),
    font=dict(size=13),
)

_LEGEND_BOTTOM = dict(
    orientation="h",
    yanchor="top",
    y=-0.18,
    xanchor="center",
    x=0.5,
    font=dict(size=12),
)


def _load_parquet(name: str) -> pl.DataFrame:
    """Load a processed Parquet file."""
    path = PROCESSED_DIR / f"ipeds_{name}.parquet"
    if not path.exists():
        msg = f"Parquet file not found: {path}. Run `make export` first."
        raise FileNotFoundError(msg)
    return pl.read_parquet(path)


def save_figure(
    fig: go.Figure,
    name: str,
    *,
    formats: list[str] | None = None,
    height: int = 700,
) -> list[Path]:
    """Save a Plotly figure in multiple formats.

    Args:
        fig: Plotly Figure to save.
        name: Base filename.
        formats: List of formats. Defaults to ["html", "png"].
        height: Image height in pixels.

    Returns:
        List of paths to saved files.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    fmts = formats or ["html", "png"]
    paths: list[Path] = []

    for fmt in fmts:
        if fmt == "html":
            p = REPORTS_DIR / f"{name}.html"
            fig.write_html(str(p), include_plotlyjs="cdn")
        elif fmt in ("png", "svg", "pdf"):
            p = REPORTS_IMAGES_DIR / f"{name}.{fmt}"
            fig.write_image(str(p), width=1200, height=height, scale=2)
        else:
            continue
        paths.append(p)

    return paths


def plot_institution_count_trends(hd: pl.DataFrame) -> go.Figure:
    """Line chart: number of institutions by sector over time.

    Args:
        hd: Combined HD DataFrame with CONTROL and SURVEY_YEAR.

    Returns:
        Plotly Figure.
    """
    counts = (
        hd.filter(pl.col("CONTROL").is_in([1, 2, 3]))
        .with_columns(pl.col("CONTROL").replace_strict(CONTROL_LABELS).alias("Sector"))
        .group_by(["SURVEY_YEAR", "Sector"])
        .len()
        .sort(["Sector", "SURVEY_YEAR"])
    )

    fig = go.Figure()
    for i, sector in enumerate(["Public", "Private Nonprofit", "Private For-Profit"]):
        sector_data = counts.filter(pl.col("Sector") == sector).sort("SURVEY_YEAR")
        fig.add_trace(
            go.Scatter(
                x=sector_data["SURVEY_YEAR"].to_list(),
                y=sector_data["len"].to_list(),
                mode="lines+markers+text",
                name=sector,
                text=[f"{v:,}" for v in sector_data["len"].to_list()],
                textposition="top center",
                textfont=dict(size=10),
                line=dict(width=3, color=COLORWAY[i]),
                marker=dict(size=8),
            )
        )

    total = hd.filter(pl.col("CONTROL").is_in([1, 2, 3])).height
    fig.update_layout(
        title=dict(
            text=(
                "US Postsecondary Institutions by Sector<br>"
                f"<sub>Source: IPEDS HD, 2018-2024 | {total:,} institution-years</sub>"
            )
        ),
        xaxis=dict(title="Academic Year", dtick=1),
        yaxis=dict(title="Number of Institutions", tickformat=","),
        legend=_LEGEND_BOTTOM,
        **_COMMON_LAYOUT,
    )
    return fig


def plot_enrollment_trends(effy: pl.DataFrame, hd: pl.DataFrame) -> go.Figure:
    """Line chart: total enrollment by sector over time.

    Args:
        effy: Combined EFFY DataFrame.
        hd: Combined HD DataFrame.

    Returns:
        Plotly Figure.
    """
    if "EFYTOTLT" not in effy.columns:
        console.print("[yellow]EFYTOTLT not found in EFFY, skipping[/yellow]")
        return go.Figure()

    # EFFYLEV=1 means all students; filter to avoid double counting
    enrollment = effy.filter(pl.col("EFFYLEV") == 1) if "EFFYLEV" in effy.columns else effy

    # Also filter LSTUDY if present (LSTUDY can cause multiple rows per inst)
    if "LSTUDY" in enrollment.columns:
        # LSTUDY=999 or the broadest level is total
        # If filtering too aggressively, just aggregate
        pass

    # Aggregate to one row per institution per year
    enr_by_inst = (
        enrollment.group_by(["UNITID", "SURVEY_YEAR"]).agg(
            pl.col("EFYTOTLT").max()
        )  # Use max to avoid double counting
    )

    hd_sector = hd.select(["UNITID", "SURVEY_YEAR", "CONTROL"]).filter(
        pl.col("CONTROL").is_in([1, 2, 3])
    )
    joined = enr_by_inst.join(hd_sector, on=["UNITID", "SURVEY_YEAR"], how="inner")

    totals = (
        joined.with_columns(pl.col("CONTROL").replace_strict(CONTROL_LABELS).alias("Sector"))
        .group_by(["SURVEY_YEAR", "Sector"])
        .agg(pl.col("EFYTOTLT").sum())
        .sort(["Sector", "SURVEY_YEAR"])
    )

    fig = go.Figure()
    for i, sector in enumerate(["Public", "Private Nonprofit", "Private For-Profit"]):
        sector_data = totals.filter(pl.col("Sector") == sector).sort("SURVEY_YEAR")
        fig.add_trace(
            go.Scatter(
                x=sector_data["SURVEY_YEAR"].to_list(),
                y=sector_data["EFYTOTLT"].to_list(),
                mode="lines+markers",
                name=sector,
                line=dict(width=3, color=COLORWAY[i]),
                marker=dict(size=8),
                hovertemplate="%{y:,.0f} students<extra>%{fullData.name}</extra>",
            )
        )

    fig.update_layout(
        title=dict(
            text=(
                "Total 12-Month Enrollment by Sector<br>"
                "<sub>Source: IPEDS EFFY (EFFYLEV=1), 2018-2024</sub>"
            )
        ),
        xaxis=dict(title="Academic Year", dtick=1),
        yaxis=dict(title="Total 12-Month Enrollment", tickformat=",.0f"),
        legend=_LEGEND_BOTTOM,
        **_COMMON_LAYOUT,
    )
    return fig


def plot_geographic_map(hd: pl.DataFrame) -> go.Figure:
    """Choropleth: institutions per state for most recent year.

    Args:
        hd: Combined HD DataFrame with STABBR.

    Returns:
        Plotly Figure.
    """
    latest_year = hd["SURVEY_YEAR"].max()
    latest = hd.filter(pl.col("SURVEY_YEAR") == latest_year)

    state_counts = (
        latest.group_by("STABBR")
        .len()
        .rename({"len": "Institutions"})
        .filter(pl.col("STABBR").str.len_chars() == 2)
        .sort("Institutions", descending=True)
    )

    top_state = state_counts.row(0)

    fig = go.Figure(
        go.Choropleth(
            locations=state_counts["STABBR"].to_list(),
            z=state_counts["Institutions"].to_list(),
            locationmode="USA-states",
            colorscale=[
                [0, PORTFOLIO_COLORS["light"]],
                [0.3, PORTFOLIO_COLORS["accent"]],
                [0.7, PORTFOLIO_COLORS["primary"]],
                [1, PORTFOLIO_COLORS["secondary"]],
            ],
            colorbar=dict(title="Institutions", thickness=15, len=0.6),
            hovertemplate="<b>%{location}</b><br>Institutions: %{z:,}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(
            text=(
                f"Postsecondary Institutions by State ({latest_year})<br>"
                f"<sub>Source: IPEDS HD | Total: {latest.height:,} institutions | "
                f"Most: {top_state[0]} ({top_state[1]:,})</sub>"
            )
        ),
        geo=dict(scope="usa", bgcolor="white", lakecolor="white"),
        **_COMMON_LAYOUT,
    )
    return fig


def plot_completions_by_level(c_df: pl.DataFrame) -> go.Figure:
    """Stacked bar: total completions by award level over time.

    Args:
        c_df: Combined Completions DataFrame.

    Returns:
        Plotly Figure.
    """
    level_labels = {
        "3": "Associate's",
        "5": "Bachelor's",
        "7": "Master's",
        "9": "Doctorate (Research)",
        "10": "Doctorate (Professional)",
    }

    if "AWLEVEL" not in c_df.columns or "CTOTALT" not in c_df.columns:
        console.print("[yellow]AWLEVEL/CTOTALT not found, skipping[/yellow]")
        return go.Figure()

    # Filter to MAJORNUM=1 if present (avoids double counting for double majors)
    filtered = c_df
    if "MAJORNUM" in c_df.columns:
        filtered = c_df.filter(pl.col("MAJORNUM") == 1)

    totals = (
        filtered.with_columns(pl.col("AWLEVEL").cast(pl.String))
        .filter(pl.col("AWLEVEL").is_in(list(level_labels.keys())))
        .with_columns(pl.col("AWLEVEL").replace_strict(level_labels).alias("Award Level"))
        .group_by(["SURVEY_YEAR", "Award Level"])
        .agg(pl.col("CTOTALT").sum())
        .sort("SURVEY_YEAR")
    )

    grand_total = totals["CTOTALT"].sum()

    # Use specific order for stacking
    level_order = [
        "Associate's",
        "Bachelor's",
        "Master's",
        "Doctorate (Research)",
        "Doctorate (Professional)",
    ]

    fig = go.Figure()
    for i, level in enumerate(level_order):
        level_data = totals.filter(pl.col("Award Level") == level).sort("SURVEY_YEAR")
        if level_data.height == 0:
            continue
        fig.add_trace(
            go.Bar(
                x=level_data["SURVEY_YEAR"].to_list(),
                y=level_data["CTOTALT"].to_list(),
                name=level,
                marker_color=COLORWAY[i],
                hovertemplate=f"{level}<br>%{{x}}: %{{y:,.0f}}<extra></extra>",
            )
        )

    fig.update_layout(
        barmode="stack",
        title=dict(
            text=(
                "Degrees Awarded by Level<br>"
                f"<sub>Source: IPEDS Completions (MAJORNUM=1), 2018-2024 | "
                f"Total: {grand_total:,.0f} awards</sub>"
            )
        ),
        xaxis=dict(title="Academic Year", dtick=1),
        yaxis=dict(title="Total Completions", tickformat=","),
        legend=_LEGEND_BOTTOM,
        **_COMMON_LAYOUT,
    )
    return fig


def plot_graduation_rate_distribution(gr: pl.DataFrame, hd: pl.DataFrame) -> go.Figure:
    """Box plot: graduation rate distribution by sector.

    IPEDS GR structure:
    - GRTYPE=2, CHRTSTAT=12: Adjusted cohort (GRTOTLT = cohort size)
    - GRTYPE=3, CHRTSTAT=13: Completers within 150% time (GRTOTLT = completers)
    Graduation rate = GRTYPE3.GRTOTLT / GRTYPE2.GRTOTLT * 100

    Args:
        gr: Combined GR DataFrame.
        hd: Combined HD DataFrame.

    Returns:
        Plotly Figure.
    """
    latest_year = gr["SURVEY_YEAR"].max()

    # Get cohort sizes (GRTYPE=2)
    cohort = gr.filter(
        (pl.col("GRTYPE") == 2)
        & (pl.col("SURVEY_YEAR") == latest_year)
        & pl.col("GRTOTLT").is_not_null()
        & (pl.col("GRTOTLT") > 0)
    ).select(["UNITID", pl.col("GRTOTLT").alias("COHORT_SIZE")])

    # Get completers (GRTYPE=3)
    completers = gr.filter(
        (pl.col("GRTYPE") == 3)
        & (pl.col("SURVEY_YEAR") == latest_year)
        & pl.col("GRTOTLT").is_not_null()
    ).select(["UNITID", pl.col("GRTOTLT").alias("COMPLETERS")])

    # Compute graduation rate
    rates = (
        cohort.join(completers, on="UNITID", how="inner")
        .with_columns((pl.col("COMPLETERS") / pl.col("COHORT_SIZE") * 100).alias("GRAD_RATE"))
        .filter((pl.col("GRAD_RATE") >= 0) & (pl.col("GRAD_RATE") <= 100))
    )

    if rates.height == 0:
        console.print("[yellow]No graduation rates computed, skipping[/yellow]")
        return go.Figure()

    # Join with HD for sector
    hd_sector = (
        hd.filter(pl.col("SURVEY_YEAR") == latest_year)
        .select(["UNITID", "CONTROL"])
        .filter(pl.col("CONTROL").is_in([1, 2, 3]))
    )
    joined = rates.join(hd_sector, on="UNITID", how="inner").with_columns(
        pl.col("CONTROL").replace_strict(CONTROL_LABELS).alias("Sector")
    )

    # Compute medians for annotations
    medians = joined.group_by("Sector").agg(pl.col("GRAD_RATE").median().alias("median"))
    overall_median = joined["GRAD_RATE"].median()

    fig = go.Figure()
    for i, sector in enumerate(["Public", "Private Nonprofit", "Private For-Profit"]):
        sector_data = joined.filter(pl.col("Sector") == sector)
        if sector_data.height == 0:
            continue
        fig.add_trace(
            go.Box(
                y=sector_data["GRAD_RATE"].to_list(),
                name=sector,
                marker_color=COLORWAY[i],
                boxmean=True,
                hoverinfo="y+name",
            )
        )

    # Add median annotations
    for row in medians.iter_rows():
        fig.add_annotation(
            x=row[0],
            y=row[1],
            text=f"Median: {row[1]:.1f}%",
            showarrow=False,
            yshift=20,
            font=dict(size=11, color=PORTFOLIO_COLORS["secondary"]),
        )

    fig.update_layout(
        title=dict(
            text=(
                f"Graduation Rate Distribution by Sector ({latest_year})<br>"
                f"<sub>Source: IPEDS GR (Bachelor's cohort, 150% time) | "
                f"N = {joined.height:,} institutions | "
                f"Overall median: {overall_median:.1f}%</sub>"
            )
        ),
        xaxis=dict(title=""),
        yaxis=dict(title="Graduation Rate (%)", range=[0, 105]),
        showlegend=False,
        **_COMMON_LAYOUT,
    )
    return fig


def plot_schema_changes_summary() -> go.Figure:
    """Bar chart: schema changes detected per component.

    Returns:
        Plotly Figure.
    """
    from src.config import INTERIM_DIR

    path = INTERIM_DIR / "schema_changes.csv"
    if not path.exists():
        console.print("[yellow]schema_changes.csv not found, skipping[/yellow]")
        return go.Figure()

    changes = pl.read_csv(path)
    total_changes = changes.height

    label_map = {
        "hd": "Institutional\nCharacteristics",
        "effy": "12-Month\nEnrollment",
        "c": "Completions",
        "gr": "Graduation\nRates",
    }

    counts = (
        changes.group_by("component")
        .len()
        .rename({"len": "Schema Changes"})
        .with_columns(pl.col("component").replace_strict(label_map).alias("Component"))
        .sort("Schema Changes", descending=True)
    )

    fig = go.Figure(
        go.Bar(
            x=counts["Component"].to_list(),
            y=counts["Schema Changes"].to_list(),
            text=counts["Schema Changes"].to_list(),
            textposition="outside",
            textfont=dict(size=16, color=PORTFOLIO_COLORS["text"]),
            marker=dict(
                color=counts["Schema Changes"].to_list(),
                colorscale=[[0, PORTFOLIO_COLORS["accent"]], [1, PORTFOLIO_COLORS["danger"]]],
            ),
            hovertemplate="%{x}<br>%{y} columns changed<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(
            text=(
                "Cross-Year Schema Changes Detected by Pipeline<br>"
                f"<sub>Automated detection across 28 CSV files, 7 years (2018-2024) | "
                f"Total: {total_changes} column-level changes</sub>"
            )
        ),
        xaxis=dict(title=""),
        yaxis=dict(
            title="Number of Column Changes",
            range=[0, max(counts["Schema Changes"].to_list()) * 1.2],
        ),
        showlegend=False,
        **_COMMON_LAYOUT,
    )
    return fig


def generate_all_visualizations() -> list[Path]:
    """Generate all dashboard visualizations from processed Parquet files.

    Returns:
        List of paths to generated files.
    """
    all_paths: list[Path] = []

    console.print("[bold]Loading processed data...[/bold]")
    hd = _load_parquet("hd")
    effy = _load_parquet("effy")
    c_df = _load_parquet("c")
    gr = _load_parquet("gr")
    console.print(f"  HD: {hd.height:,} rows | EFFY: {effy.height:,} rows")
    console.print(f"  C: {c_df.height:,} rows | GR: {gr.height:,} rows")

    charts: list[tuple[str, go.Figure]] = [
        ("01_institution_count_trends", plot_institution_count_trends(hd)),
        ("02_enrollment_trends", plot_enrollment_trends(effy, hd)),
        ("03_geographic_map", plot_geographic_map(hd)),
        ("04_completions_by_level", plot_completions_by_level(c_df)),
        ("05_graduation_rate_distribution", plot_graduation_rate_distribution(gr, hd)),
        ("06_schema_changes_summary", plot_schema_changes_summary()),
    ]

    for name, fig in charts:
        if fig.data:
            console.print(f"\n[bold blue]Generating {name}...[/bold blue]")
            paths = save_figure(fig, name)
            for p in paths:
                console.print(f"  {p.name}")
            all_paths.extend(paths)
        else:
            console.print(f"\n[yellow]Skipped {name} (no data)[/yellow]")

    return all_paths


if __name__ == "__main__":
    console.print("[bold]IPEDS Visualization Generator[/bold]\n")

    paths = generate_all_visualizations()

    console.print(f"\n[bold green]Generated {len(paths)} visualization files![/bold green]")
    console.print(f"  HTML reports: {REPORTS_DIR}")
    console.print(f"  PNG images: {REPORTS_IMAGES_DIR}")
