"""Data ingestion module for IPEDS raw CSV files.

Handles reading raw IPEDS CSVs with proper encoding detection,
null value mapping, and metadata extraction.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl

from src.config import ENCODING_PRIORITY, NULL_VALUES, RAW_DIR, SURVEY_COMPONENTS, SURVEY_YEARS

if TYPE_CHECKING:
    pass


def read_csv_with_fallback(
    path: Path,
    *,
    null_values: list[str] | None = None,
    infer_schema_length: int = 10000,
) -> pl.DataFrame:
    """Read a CSV file with encoding fallback.

    Args:
        path: Path to the CSV file.
        null_values: Values to treat as null. Defaults to IPEDS null codes.
        infer_schema_length: Number of rows for schema inference.

    Returns:
        Polars DataFrame with the CSV contents.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If no encoding succeeds.
    """
    raise NotImplementedError


def discover_raw_files(raw_dir: Path | None = None) -> dict[str, list[Path]]:
    """Discover all raw IPEDS CSV files organized by survey component.

    Args:
        raw_dir: Directory containing raw CSVs. Defaults to config RAW_DIR.

    Returns:
        Dictionary mapping component prefix to list of CSV paths.
    """
    raise NotImplementedError


def ingest_component(
    component: str,
    years: list[int] | None = None,
    raw_dir: Path | None = None,
) -> dict[int, pl.DataFrame]:
    """Ingest all years of a single IPEDS survey component.

    Args:
        component: Survey component prefix (e.g., "hd", "ef", "c", "gr").
        years: List of years to ingest. Defaults to all configured years.
        raw_dir: Directory containing raw CSVs. Defaults to config RAW_DIR.

    Returns:
        Dictionary mapping year to DataFrame for the given component.
    """
    raise NotImplementedError


def ingest_all(raw_dir: Path | None = None) -> dict[str, dict[int, pl.DataFrame]]:
    """Ingest all survey components across all years.

    Args:
        raw_dir: Directory containing raw CSVs. Defaults to config RAW_DIR.

    Returns:
        Nested dictionary: component -> year -> DataFrame.
    """
    raise NotImplementedError


def get_file_metadata(path: Path) -> dict[str, str | int]:
    """Extract metadata from a raw CSV file.

    Args:
        path: Path to the CSV file.

    Returns:
        Dictionary with keys: filename, size_bytes, row_count,
        column_count, encoding_detected.
    """
    raise NotImplementedError


if __name__ == "__main__":
    print(f"IPEDS Ingest: scanning {RAW_DIR}")
    print(f"Survey components: {list(SURVEY_COMPONENTS.keys())}")
    print(f"Years: {SURVEY_YEARS}")
    print("Not yet implemented -- run after downloading IPEDS data.")
