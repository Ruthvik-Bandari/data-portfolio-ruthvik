"""Schema harmonization module for IPEDS cross year data.

Maps column names across survey years to canonical names, handles
type coercion rules, and applies YAML-defined schema definitions.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl

from src.config import SCHEMAS_DIR

if TYPE_CHECKING:
    pass


def load_schema_mapping(component: str, schema_dir: Path | None = None) -> dict:
    """Load the YAML schema mapping for a survey component.

    Args:
        component: Survey component prefix (e.g., "hd", "ef").
        schema_dir: Directory containing YAML schema files.

    Returns:
        Dictionary with canonical columns, year mappings, and coercions.
    """
    raise NotImplementedError


def build_column_mapping(
    source_columns: list[str], year: int, component: str,
) -> dict[str, str]:
    """Build a column rename mapping for a specific year.

    Args:
        source_columns: Column names from the source DataFrame.
        year: The survey year.
        component: Survey component prefix.

    Returns:
        Dictionary mapping original names to canonical names.
    """
    raise NotImplementedError


def apply_column_mapping(df: pl.DataFrame, mapping: dict[str, str]) -> pl.DataFrame:
    """Rename columns in a DataFrame according to a mapping.

    Args:
        df: Source DataFrame.
        mapping: Dictionary mapping old names to new names.

    Returns:
        DataFrame with renamed columns.
    """
    raise NotImplementedError


def apply_type_coercions(
    df: pl.DataFrame, coercions: dict[str, pl.DataType],
) -> pl.DataFrame:
    """Apply type coercion rules to a DataFrame.

    Args:
        df: Source DataFrame.
        coercions: Dictionary mapping column names to target Polars types.

    Returns:
        DataFrame with coerced column types.
    """
    raise NotImplementedError


def harmonize_component(
    dataframes: dict[int, pl.DataFrame], component: str,
) -> dict[int, pl.DataFrame]:
    """Harmonize all years of a single survey component.

    Args:
        dataframes: Dictionary mapping year to raw DataFrame.
        component: Survey component prefix.

    Returns:
        Dictionary mapping year to harmonized DataFrame.
    """
    raise NotImplementedError


def generate_schema_yaml(
    dataframes: dict[int, pl.DataFrame],
    component: str,
    output_path: Path | None = None,
) -> Path:
    """Auto generate a YAML schema definition from existing data.

    Args:
        dataframes: Dictionary mapping year to DataFrame.
        component: Survey component prefix.
        output_path: Path to write the YAML file.

    Returns:
        Path to the generated YAML schema file.
    """
    raise NotImplementedError


if __name__ == "__main__":
    print(f"IPEDS Harmonizer: schema definitions at {SCHEMAS_DIR}")
    print("Not yet implemented -- run after profiling phase.")
