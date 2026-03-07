"""Schema harmonization module for IPEDS cross year data.

Normalizes column names, applies type coercions, generates YAML
schema definitions, and ensures consistent structure across all
years of IPEDS data.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
import yaml
from rich.console import Console

from src.config import (
    NULL_VALUES,
    PRIMARY_KEY,
    SCHEMAS_DIR,
    SURVEY_COMPONENTS,
)

console = Console()


def normalize_columns(df: pl.DataFrame) -> pl.DataFrame:
    """Normalize column names: strip whitespace, uppercase.

    IPEDS uses uppercase column names. Some years have trailing spaces
    in column names (e.g., 'EFYGUKN ' in 2022). This standardizes all
    column names.

    Args:
        df: Source DataFrame.

    Returns:
        DataFrame with normalized column names.
    """
    rename_map = {col: col.strip().upper() for col in df.columns}
    return df.rename(rename_map)


def apply_column_mapping(df: pl.DataFrame, mapping: dict[str, str]) -> pl.DataFrame:
    """Rename columns in a DataFrame according to a mapping.

    Only renames columns that exist in the DataFrame and in the mapping.

    Args:
        df: Source DataFrame.
        mapping: Dictionary mapping old names to new names.

    Returns:
        DataFrame with renamed columns.
    """
    existing = {k: v for k, v in mapping.items() if k in df.columns}
    if existing:
        return df.rename(existing)
    return df


def apply_type_coercions(
    df: pl.DataFrame,
    coercions: dict[str, pl.DataType],
) -> pl.DataFrame:
    """Apply type coercion rules to a DataFrame.

    Uses strict=False so values that cannot be cast become null
    instead of raising errors.

    Args:
        df: Source DataFrame.
        coercions: Dictionary mapping column names to target Polars types.

    Returns:
        DataFrame with coerced column types.
    """
    cast_exprs = []
    for col_name, target_type in coercions.items():
        if col_name in df.columns and df[col_name].dtype != target_type:
            cast_exprs.append(pl.col(col_name).cast(target_type, strict=False))

    if cast_exprs:
        return df.with_columns(cast_exprs)
    return df


def build_type_coercions(
    dataframes: dict[int, pl.DataFrame],
) -> dict[str, pl.DataType]:
    """Determine canonical types for each column across years.

    For columns with inconsistent types, uses the most common type.
    Prefers Int64 over String for numeric columns that are sometimes
    read as strings.

    Args:
        dataframes: Dictionary mapping year to DataFrame.

    Returns:
        Dictionary mapping column names to canonical Polars types.
    """
    type_votes: dict[str, dict[str, int]] = {}

    for df in dataframes.values():
        for col_name in df.columns:
            dtype_str = str(df[col_name].dtype)
            if col_name not in type_votes:
                type_votes[col_name] = {}
            type_votes[col_name][dtype_str] = type_votes[col_name].get(dtype_str, 0) + 1

    coercions: dict[str, pl.DataType] = {}
    for col_name, votes in type_votes.items():
        if len(votes) <= 1:
            continue

        # If both Int64 and String appear, prefer Int64 (String is likely
        # a misparse of numeric data)
        if "Int64" in votes and "String" in votes:
            coercions[col_name] = pl.Int64
        elif "Float64" in votes:
            coercions[col_name] = pl.Float64
        else:
            # Use the most common type
            winner = max(votes, key=lambda k: votes[k])
            dtype_map = {
                "Int64": pl.Int64,
                "Float64": pl.Float64,
                "String": pl.String,
                "Boolean": pl.Boolean,
            }
            if winner in dtype_map:
                coercions[col_name] = dtype_map[winner]

    return coercions


def harmonize_component(
    dataframes: dict[int, pl.DataFrame],
    component: str,
) -> dict[int, pl.DataFrame]:
    """Harmonize all years of a single survey component.

    Steps:
    1. Normalize column names (strip whitespace, uppercase)
    2. Determine and apply type coercions for consistency
    3. Standardize null values
    4. Add survey_year column

    Args:
        dataframes: Dictionary mapping year to raw DataFrame.
        component: Survey component prefix.

    Returns:
        Dictionary mapping year to harmonized DataFrame.
    """
    # Step 1: Normalize column names across all years
    normalized = {year: normalize_columns(df) for year, df in dataframes.items()}

    # Step 2: Build and apply type coercions
    coercions = build_type_coercions(normalized)
    if coercions:
        console.print(f"  Type coercions needed: {len(coercions)} columns")
        for col, dtype in coercions.items():
            console.print(f"    {col} -> {dtype}")

    result: dict[int, pl.DataFrame] = {}
    for year, df in normalized.items():
        # Apply type coercions
        df = apply_type_coercions(df, coercions)

        # Standardize remaining null-like string values
        str_cols = [c for c in df.columns if df[c].dtype == pl.String]
        if str_cols:
            null_exprs = [
                pl.when(pl.col(c).is_in(NULL_VALUES)).then(None).otherwise(pl.col(c)).alias(c)
                for c in str_cols
            ]
            df = df.with_columns(null_exprs)

        # Add survey year
        df = df.with_columns(pl.lit(year).alias("SURVEY_YEAR"))

        result[year] = df

    return result


def harmonize_all(
    data: dict[str, dict[int, pl.DataFrame]],
) -> dict[str, dict[int, pl.DataFrame]]:
    """Harmonize all components across all years.

    Args:
        data: Nested dictionary from ingest_all: component -> year -> DataFrame.

    Returns:
        Same structure with harmonized DataFrames.
    """
    result: dict[str, dict[int, pl.DataFrame]] = {}
    for component, years_data in data.items():
        label = SURVEY_COMPONENTS.get(component, component)
        console.print(f"\n[bold blue]Harmonizing {label} ({component.upper()})[/bold blue]")
        result[component] = harmonize_component(years_data, component)
        console.print(f"  [green]Done: {len(result[component])} years harmonized[/green]")
    return result


def generate_schema_yaml(
    dataframes: dict[int, pl.DataFrame],
    component: str,
    output_path: Path | None = None,
) -> Path:
    """Auto generate a YAML schema definition from profiled data.

    Creates a comprehensive schema showing each column's presence
    and type across all years, useful for documentation and review.

    Args:
        dataframes: Dictionary mapping year to DataFrame.
        component: Survey component prefix.
        output_path: Path to write the YAML file.

    Returns:
        Path to the generated YAML schema file.
    """
    out = output_path or (SCHEMAS_DIR / f"{component}_schema.yaml")
    out.parent.mkdir(parents=True, exist_ok=True)

    # Collect column info across years
    all_columns: dict[str, dict] = {}
    for year, df in sorted(dataframes.items()):
        for col_name in df.columns:
            if col_name == "SURVEY_YEAR":
                continue
            if col_name not in all_columns:
                all_columns[col_name] = {"years_present": [], "types": {}}
            all_columns[col_name]["years_present"].append(year)
            all_columns[col_name]["types"][str(year)] = str(df[col_name].dtype)

    schema: dict = {
        "component": component,
        "label": SURVEY_COMPONENTS.get(component, component),
        "primary_key": PRIMARY_KEY,
        "columns": {},
    }

    for col_name in sorted(all_columns.keys()):
        info = all_columns[col_name]
        years = info["years_present"]
        types_set = set(info["types"].values())
        schema["columns"][col_name] = {
            "present_in": years,
            "types_observed": list(types_set),
            "consistent_type": len(types_set) == 1,
            "all_years": len(years) == len(dataframes),
        }

    with open(out, "w") as f:
        yaml.dump(schema, f, default_flow_style=False, sort_keys=False)

    return out


def generate_all_schemas(
    data: dict[str, dict[int, pl.DataFrame]],
) -> list[Path]:
    """Generate YAML schemas for all components.

    Args:
        data: Nested dictionary from harmonize_all.

    Returns:
        List of paths to generated YAML schema files.
    """
    paths: list[Path] = []
    for component, years_data in data.items():
        path = generate_schema_yaml(years_data, component)
        console.print(f"  Schema saved: {path.name}")
        paths.append(path)
    return paths


if __name__ == "__main__":
    from src.ingest import ingest_all

    console.print("[bold]IPEDS Schema Harmonization[/bold]\n")

    # Step 1: Ingest
    console.print("[bold]Step 1: Ingesting raw data...[/bold]")
    raw_data = ingest_all()

    # Step 2: Harmonize
    console.print("\n[bold]Step 2: Harmonizing schemas...[/bold]")
    harmonized = harmonize_all(raw_data)

    # Step 3: Generate YAML schemas
    console.print("\n[bold]Step 3: Generating YAML schemas...[/bold]")
    schema_paths = generate_all_schemas(harmonized)

    # Step 4: Summary
    console.print("\n[bold]Summary:[/bold]")
    for component, years_data in harmonized.items():
        label = SURVEY_COMPONENTS.get(component, component)
        sample = next(iter(years_data.values()))
        console.print(f"  {label}: {sample.width} columns (harmonized)")

    console.print("\n[bold green]Harmonization complete![/bold green]")
