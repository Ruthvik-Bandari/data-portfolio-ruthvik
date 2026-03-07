"""Visualization module for IPEDS dashboard charts.

Generates interactive Plotly charts from the processed IPEDS data.
All charts use the portfolio consistent theme and are exported as
self contained HTML files and static PNG images.

Key IPEDS columns used:
- HD: UNITID, INSTNM, STABBR, CONTROL, ICLEVEL, INSTSIZE, LONGITUD, LATITUDE
  CONTROL: 1=Public, 2=Private nonprofit, 3=Private for-profit
- EFFY: UNITID, EFYTOTLT (total enrollment), EFFYLEV (level)
- GR: UNITID, GRTOTLT (graduation rate total cohort), GRTYPE
- C: UNITID, CTOTALT (total completions), AWLEVEL (award level)
"""

from __future__ import annotations

from pathlib import Path

import plotly.express as px
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
) -> list[Path]:
    """Save a Plotly figure in multiple formats.

    Args:
        fig: Plotly Figure to save.
        name: Base filename.
        formats: List of formats. Defaults to ["html", "png"].

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
            fig.write_image(str(p), width=1200, height=600, scale=2)
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
        .sort("SURVEY_YEAR")
    )

    fig = px.line(
        counts.to_pandas(),
        x="SURVEY_YEAR",
        y="len",
        color="Sector",
        markers=True,
        title="US Postsecondary Institutions by Sector (2018-2024)",
        labels={"SURVEY_YEAR": "Year", "len": "Number of Institutions"},
        color_discrete_sequence=COLORWAY,
    )
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig


def plot_enrollment_trends(effy: pl.DataFrame, hd: pl.DataFrame) -> go.Figure:
    """Line chart: total enrollment by sector over time.

    Joins EFFY enrollment totals with HD sector information.

    Args:
        effy: Combined EFFY DataFrame.
        hd: Combined HD DataFrame.

    Returns:
        Plotly Figure.
    """
    # EFFYLEV=1 is all students; EFYTOTLT is total enrollment
    enrollment = effy.filter(pl.col("EFFYLEV") == 1)

    if "EFYTOTLT" not in enrollment.columns:
        console.print("[yellow]EFYTOTLT not found in EFFY, skipping enrollment trends[/yellow]")
        return go.Figure()

    # Aggregate enrollment per institution per year
    enr_by_inst = enrollment.group_by(["UNITID", "SURVEY_YEAR"]).agg(pl.col("EFYTOTLT").sum())

    # Join with HD for sector info
    hd_sector = hd.select(["UNITID", "SURVEY_YEAR", "CONTROL"]).filter(
        pl.col("CONTROL").is_in([1, 2, 3])
    )
    joined = enr_by_inst.join(hd_sector, on=["UNITID", "SURVEY_YEAR"], how="inner")

    totals = (
        joined.with_columns(pl.col("CONTROL").replace_strict(CONTROL_LABELS).alias("Sector"))
        .group_by(["SURVEY_YEAR", "Sector"])
        .agg(pl.col("EFYTOTLT").sum())
        .sort("SURVEY_YEAR")
    )

    fig = px.line(
        totals.to_pandas(),
        x="SURVEY_YEAR",
        y="EFYTOTLT",
        color="Sector",
        markers=True,
        title="Total 12-Month Enrollment by Sector (2018-2024)",
        labels={"SURVEY_YEAR": "Year", "EFYTOTLT": "Total Enrollment"},
        color_discrete_sequence=COLORWAY,
    )
    fig.update_layout(
        yaxis_tickformat=",",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
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
        .rename({"len": "Institution Count"})
        .filter(pl.col("STABBR").str.len_chars() == 2)
    )

    fig = px.choropleth(
        state_counts.to_pandas(),
        locations="STABBR",
        locationmode="USA-states",
        color="Institution Count",
        scope="usa",
        title=f"Postsecondary Institutions by State ({latest_year})",
        color_continuous_scale=[PORTFOLIO_COLORS["light"], PORTFOLIO_COLORS["primary"]],
    )
    fig.update_layout(geo=dict(bgcolor="white"))
    return fig


def plot_completions_by_level(c_df: pl.DataFrame) -> go.Figure:
    """Stacked bar: total completions by award level over time.

    AWLEVEL codes: 1=Certificate<1yr, 2=Certificate1-2yr, 3=Associate,
    5=Bachelor, 7=Master, 9=Doctor-Research, etc.

    Args:
        c_df: Combined Completions DataFrame.

    Returns:
        Plotly Figure.
    """
    level_labels = {
        "1": "Certificate (<1yr)",
        "2": "Certificate (1-2yr)",
        "3": "Associate",
        "5": "Bachelor's",
        "7": "Master's",
        "8": "Post-Master's",
        "9": "Doctor's (Research)",
        "10": "Doctor's (Professional)",
        "11": "Doctor's (Other)",
    }

    if "AWLEVEL" not in c_df.columns or "CTOTALT" not in c_df.columns:
        console.print("[yellow]AWLEVEL/CTOTALT not found, skipping completions chart[/yellow]")
        return go.Figure()

    # Filter to main award levels and aggregate
    totals = (
        c_df.with_columns(pl.col("AWLEVEL").cast(pl.String))
        .filter(pl.col("AWLEVEL").is_in(list(level_labels.keys())))
        .with_columns(pl.col("AWLEVEL").replace_strict(level_labels).alias("Award Level"))
        .group_by(["SURVEY_YEAR", "Award Level"])
        .agg(pl.col("CTOTALT").sum())
        .sort("SURVEY_YEAR")
    )

    fig = px.bar(
        totals.to_pandas(),
        x="SURVEY_YEAR",
        y="CTOTALT",
        color="Award Level",
        title="Completions by Award Level (2018-2024)",
        labels={"SURVEY_YEAR": "Year", "CTOTALT": "Total Completions"},
        color_discrete_sequence=COLORWAY,
        barmode="stack",
    )
    fig.update_layout(
        yaxis_tickformat=",",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def plot_graduation_rate_distribution(gr: pl.DataFrame, hd: pl.DataFrame) -> go.Figure:
    """Box plot: graduation rate distribution by sector.

    Uses GRTYPE=2 (Bachelor's seeking, 4-year) and GRTOTLT (total cohort
    graduation rate).

    Args:
        gr: Combined GR DataFrame.
        hd: Combined HD DataFrame.

    Returns:
        Plotly Figure.
    """
    if "GRTOTLT" not in gr.columns:
        console.print("[yellow]GRTOTLT not found, skipping graduation rate chart[/yellow]")
        return go.Figure()

    # GRTYPE=2 is typically the bachelor's degree seeking cohort
    gr_filtered = gr.filter(
        (pl.col("GRTYPE") == 2) & pl.col("GRTOTLT").is_not_null() & (pl.col("GRTOTLT") > 0)
    )

    latest_year = gr_filtered["SURVEY_YEAR"].max()
    gr_latest = gr_filtered.filter(pl.col("SURVEY_YEAR") == latest_year)

    # Join with HD for sector
    hd_sector = (
        hd.filter(pl.col("SURVEY_YEAR") == latest_year)
        .select(["UNITID", "CONTROL"])
        .filter(pl.col("CONTROL").is_in([1, 2, 3]))
    )
    joined = gr_latest.join(hd_sector, on="UNITID", how="inner").with_columns(
        pl.col("CONTROL").replace_strict(CONTROL_LABELS).alias("Sector")
    )

    fig = px.box(
        joined.to_pandas(),
        x="Sector",
        y="GRTOTLT",
        color="Sector",
        title=f"Graduation Rate Distribution by Sector ({latest_year})",
        labels={"GRTOTLT": "Graduation Rate (%)"},
        color_discrete_sequence=COLORWAY,
    )
    fig.update_layout(showlegend=False)
    return fig


def plot_schema_changes_summary() -> go.Figure:
    """Bar chart: number of schema changes detected per component.

    Reads from the interim schema_changes.csv generated by profiling.

    Returns:
        Plotly Figure.
    """
    from src.config import INTERIM_DIR

    path = INTERIM_DIR / "schema_changes.csv"
    if not path.exists():
        console.print("[yellow]schema_changes.csv not found, skipping[/yellow]")
        return go.Figure()

    changes = pl.read_csv(path)
    counts = (
        changes.group_by("component")
        .len()
        .rename({"len": "Schema Changes"})
        .with_columns(
            pl.col("component")
            .replace_strict(
                {
                    "hd": "Institutional\nCharacteristics",
                    "effy": "12-Month\nEnrollment",
                    "c": "Completions",
                    "gr": "Graduation\nRates",
                }
            )
            .alias("Component")
        )
        .sort("Schema Changes", descending=True)
    )

    fig = px.bar(
        counts.to_pandas(),
        x="Component",
        y="Schema Changes",
        title="Cross-Year Schema Changes Detected per Component",
        color="Schema Changes",
        color_continuous_scale=[PORTFOLIO_COLORS["accent"], PORTFOLIO_COLORS["danger"]],
        text="Schema Changes",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False)
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
        if fig.data:  # Skip empty figures
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
