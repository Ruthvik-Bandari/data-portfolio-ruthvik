"""Data profiling module for IPEDS datasets.

Automates schema detection, type distribution analysis, null rate
computation, and cross year schema comparison.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
from rich.console import Console
from rich.table import Table

from src.config import INTERIM_DIR, SURVEY_COMPONENTS
from src.ingest import discover_raw_files, ingest_all, read_csv_with_fallback

console = Console()


def profile_dataframe(df: pl.DataFrame, source_label: str = "") -> pl.DataFrame:
    """Generate a profiling summary for a single DataFrame.

    Args:
        df: The DataFrame to profile.
        source_label: Optional label to include in output.

    Returns:
        DataFrame with one row per column containing profiling metrics.
    """
    rows: list[dict] = []
    for col_name in df.columns:
        col = df[col_name]
        row: dict = {
            "source": source_label,
            "column_name": col_name,
            "dtype": str(col.dtype),
            "null_count": col.null_count(),
            "null_rate": round(col.null_count() / df.height, 4) if df.height > 0 else 0.0,
            "n_unique": col.n_unique(),
            "total_rows": df.height,
        }

        # Add min/max for numeric columns
        if col.dtype.is_numeric():
            non_null = col.drop_nulls()
            if non_null.len() > 0:
                row["min_value"] = str(non_null.min())
                row["max_value"] = str(non_null.max())
            else:
                row["min_value"] = None
                row["max_value"] = None
        else:
            row["min_value"] = None
            row["max_value"] = None

        # Sample values (first 3 non null)
        non_null_sample = col.drop_nulls().head(3).to_list()
        row["sample_values"] = str(non_null_sample[:3])

        rows.append(row)

    return pl.DataFrame(rows)


def profile_all_files(raw_dir: Path | None = None) -> pl.DataFrame:
    """Profile all discovered raw CSV files.

    Args:
        raw_dir: Directory containing raw CSVs.

    Returns:
        Combined profiling DataFrame with a source column.
    """
    discovered = discover_raw_files(raw_dir)
    all_profiles: list[pl.DataFrame] = []

    for component, year_paths in discovered.items():
        label = SURVEY_COMPONENTS.get(component, component)
        console.print(f"\n[bold blue]▶ Profiling {label}[/bold blue]")

        for year, path in sorted(year_paths.items()):
            console.print(f"  Profiling {path.name}...", end=" ")
            df = read_csv_with_fallback(path)
            profile = profile_dataframe(df, source_label=path.name)
            profile = profile.with_columns(
                pl.lit(component).alias("component"),
                pl.lit(year).alias("year"),
            )
            all_profiles.append(profile)
            console.print(f"[green]{df.width} columns[/green]")

    if not all_profiles:
        return pl.DataFrame()

    return pl.concat(all_profiles, how="diagonal")


def compare_schemas_across_years(
    data: dict[str, dict[int, pl.DataFrame]],
) -> pl.DataFrame:
    """Generate a cross year schema comparison for all components.

    Args:
        data: Nested dictionary from ingest_all: component -> year -> DataFrame.

    Returns:
        DataFrame showing column presence and dtype per component/year.
    """
    rows: list[dict] = []

    for component, years_data in data.items():
        # Collect all unique column names across years
        all_columns: set[str] = set()
        for df in years_data.values():
            all_columns.update(df.columns)

        for col_name in sorted(all_columns):
            row: dict = {"component": component, "column_name": col_name}
            for year in sorted(years_data.keys()):
                df = years_data[year]
                if col_name in df.columns:
                    row[f"present_{year}"] = True
                    row[f"dtype_{year}"] = str(df[col_name].dtype)
                else:
                    row[f"present_{year}"] = False
                    row[f"dtype_{year}"] = None
            rows.append(row)

    return pl.DataFrame(rows)


def find_schema_changes(schema_comparison: pl.DataFrame) -> pl.DataFrame:
    """Identify columns whose presence or type changes across years.

    Args:
        schema_comparison: Output from compare_schemas_across_years.

    Returns:
        Filtered DataFrame showing only columns with cross year differences.
    """
    present_cols = [c for c in schema_comparison.columns if c.startswith("present_")]
    dtype_cols = [c for c in schema_comparison.columns if c.startswith("dtype_")]

    changed_rows: list[int] = []
    for i in range(schema_comparison.height):
        # Check if presence varies
        presences = [schema_comparison[c][i] for c in present_cols]
        if len(set(presences)) > 1:
            changed_rows.append(i)
            continue

        # Check if dtype varies (only among years where present)
        dtypes = [
            schema_comparison[c][i]
            for c, p in zip(dtype_cols, present_cols, strict=True)
            if schema_comparison[p][i]
        ]
        if len(set(dtypes)) > 1:
            changed_rows.append(i)

    if not changed_rows:
        return schema_comparison.head(0)  # empty with same schema

    return schema_comparison[changed_rows]


def compute_null_rates(df: pl.DataFrame) -> pl.DataFrame:
    """Compute null rates for every column in a DataFrame.

    Args:
        df: The DataFrame to analyze.

    Returns:
        DataFrame with columns: column_name, null_count, total_rows, null_rate.
    """
    return pl.DataFrame(
        {
            "column_name": df.columns,
            "null_count": [df[c].null_count() for c in df.columns],
            "total_rows": [df.height] * df.width,
            "null_rate": [
                round(df[c].null_count() / df.height, 4) if df.height > 0 else 0.0
                for c in df.columns
            ],
        }
    ).sort("null_rate", descending=True)


def print_schema_summary(
    data: dict[str, dict[int, pl.DataFrame]],
) -> None:
    """Print a rich summary of schema variations across years.

    Args:
        data: Nested dictionary from ingest_all.
    """
    for component, years_data in data.items():
        label = SURVEY_COMPONENTS.get(component, component)
        table = Table(title=f"{label} ({component.upper()}) — Schema Summary")
        table.add_column("Year", style="bold")
        table.add_column("Rows", justify="right")
        table.add_column("Columns", justify="right")
        table.add_column("Null Rate", justify="right")

        for year in sorted(years_data.keys()):
            df = years_data[year]
            null_counts = df.null_count().row(0)
            total_nulls = sum(null_counts)
            total_cells = df.height * df.width
            null_rate = round(total_nulls / total_cells * 100, 1) if total_cells > 0 else 0.0

            table.add_row(
                str(year),
                f"{df.height:,}",
                str(df.width),
                f"{null_rate}%",
            )

        console.print()
        console.print(table)


if __name__ == "__main__":
    console.print("[bold]IPEDS Data Profiling[/bold]\n")

    # Step 1: Ingest all data
    console.print("[bold]Step 1: Ingesting raw data...[/bold]")
    data = ingest_all()

    # Step 2: Print schema summary
    console.print("\n[bold]Step 2: Schema summary per component...[/bold]")
    print_schema_summary(data)

    # Step 3: Cross year schema comparison
    console.print("\n[bold]Step 3: Cross year schema comparison...[/bold]")
    schema_comp = compare_schemas_across_years(data)

    # Step 4: Find schema changes
    changes = find_schema_changes(schema_comp)
    if changes.height > 0:
        console.print(f"\n[yellow]Found {changes.height} columns with cross year changes[/yellow]")
        # Save to interim
        INTERIM_DIR.mkdir(parents=True, exist_ok=True)
        changes.write_csv(INTERIM_DIR / "schema_changes.csv")
        console.print(f"  Saved to {INTERIM_DIR / 'schema_changes.csv'}")
    else:
        console.print("\n[green]No schema changes detected across years[/green]")

    # Step 5: Full schema comparison export
    schema_comp.write_csv(INTERIM_DIR / "schema_comparison.csv")
    console.print(f"  Full comparison: {INTERIM_DIR / 'schema_comparison.csv'}")

    # Step 6: Profile all files
    console.print("\n[bold]Step 4: Detailed column profiling...[/bold]")
    profiles = profile_all_files()
    if profiles.height > 0:
        profiles.write_csv(INTERIM_DIR / "column_profiles.csv")
        console.print(f"\n  Profiles saved: {INTERIM_DIR / 'column_profiles.csv'}")
        console.print(f"  Total columns profiled: {profiles.height}")

    console.print("\n[bold green]✓ Profiling complete![/bold green]")
