"""Data combination module for IPEDS datasets.

Joins survey components on UNITID within each year, then stacks
multi year data with a survey_year column to create the final
combined analytical dataset.
"""

from __future__ import annotations

import polars as pl
from rich.console import Console

from src.config import PRIMARY_KEY, SURVEY_COMPONENTS

console = Console()


def join_components_for_year(
    components: dict[str, pl.DataFrame],
    year: int,
    join_key: str = PRIMARY_KEY,
) -> pl.DataFrame:
    """Join multiple survey components for a single year.

    Uses HD (Institutional Characteristics) as the base table
    and left-joins other components onto it.

    Args:
        components: Dictionary mapping component prefix to DataFrame.
        year: The survey year.
        join_key: Column to join on. Defaults to UNITID.

    Returns:
        Combined DataFrame with all components joined.
    """
    # HD is the base — every institution should be here
    if "hd" not in components:
        msg = f"HD component missing for year {year}"
        raise ValueError(msg)

    base = components["hd"]

    # Join other components with suffixes to avoid column name collisions
    for comp_key, comp_df in components.items():
        if comp_key == "hd":
            continue

        if join_key not in comp_df.columns:
            console.print(f"    [yellow]Skipping {comp_key}: no {join_key} column[/yellow]")
            continue

        # For multi-row components (EFFY, C, GR), we aggregate first
        # to get one row per institution before joining to HD
        if comp_df.group_by(join_key).len().filter(pl.col("len") > 1).height > 0:
            # This component has multiple rows per institution
            # We'll skip joining it directly — it stays separate
            # for detailed analysis. Only join single-row-per-institution data.
            console.print(
                f"    [dim]{comp_key}: multi-row per institution, "
                f"skipping join (kept separate)[/dim]"
            )
            continue

        # Find overlapping columns (excluding join key and SURVEY_YEAR)
        overlap = set(base.columns) & set(comp_df.columns) - {join_key, "SURVEY_YEAR"}
        if overlap:
            # Add component prefix to avoid collisions
            rename = {c: f"{comp_key}_{c}" for c in overlap}
            comp_df = comp_df.rename(rename)

        # Drop SURVEY_YEAR from the joining table (base already has it)
        if "SURVEY_YEAR" in comp_df.columns:
            comp_df = comp_df.drop("SURVEY_YEAR")

        base = base.join(comp_df, on=join_key, how="left")
        console.print(f"    Joined {comp_key}: {base.width} cols after join")

    return base


def stack_years(
    yearly_frames: dict[int, pl.DataFrame],
) -> pl.DataFrame:
    """Stack multiple years of data vertically.

    Uses Polars diagonal concatenation to handle columns that may
    exist in some years but not others (fills missing with null).

    Args:
        yearly_frames: Dictionary mapping year to DataFrame.

    Returns:
        Single DataFrame with all years stacked.
    """
    frames = [df for _, df in sorted(yearly_frames.items())]
    if not frames:
        return pl.DataFrame()

    return pl.concat(frames, how="diagonal")


def combine_all(
    cleaned_data: dict[str, dict[int, pl.DataFrame]],
) -> dict[str, pl.DataFrame]:
    """Stack each component across all years.

    Rather than joining all components into one massive table (which
    doesn't work well when some components have multiple rows per
    institution), we stack each component across years independently.
    This produces one combined DataFrame per component, each with
    a SURVEY_YEAR column.

    Args:
        cleaned_data: Nested dictionary of component -> year -> DataFrame.

    Returns:
        Dictionary mapping component to combined multi-year DataFrame.
    """
    result: dict[str, pl.DataFrame] = {}

    for component, years_data in cleaned_data.items():
        label = SURVEY_COMPONENTS.get(component, component)
        console.print(f"\n[bold blue]Combining {label} ({component.upper()})[/bold blue]")

        combined = stack_years(years_data)
        combined = combined.sort([PRIMARY_KEY, "SURVEY_YEAR"])

        result[component] = combined
        console.print(
            f"  [green]Combined: {combined.height:,} rows x "
            f"{combined.width} cols ({len(years_data)} years)[/green]"
        )

    return result


if __name__ == "__main__":
    from src.clean import clean_all
    from src.harmonize import harmonize_all
    from src.ingest import ingest_all

    console.print("[bold]IPEDS Data Combination[/bold]\n")

    console.print("[bold]Step 1: Ingest...[/bold]")
    raw = ingest_all()

    console.print("\n[bold]Step 2: Harmonize...[/bold]")
    harmonized = harmonize_all(raw)

    console.print("\n[bold]Step 3: Clean...[/bold]")
    cleaned = clean_all(harmonized)

    console.print("\n[bold]Step 4: Combine...[/bold]")
    combined = combine_all(cleaned)

    console.print("\n[bold]Final datasets:[/bold]")
    for component, df in combined.items():
        label = SURVEY_COMPONENTS.get(component, component)
        console.print(f"  {label}: {df.height:,} rows x {df.width} cols")

    console.print("\n[bold green]Combination complete![/bold green]")
