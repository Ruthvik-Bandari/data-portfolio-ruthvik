"""Data export module for IPEDS pipeline outputs.

Exports the final combined dataset in Parquet, CSV, and
BI tool optimized formats.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl

from src.config import PROCESSED_DIR

if TYPE_CHECKING:
    pass


def export_parquet(
    df: pl.DataFrame, output_path: Path | None = None, *, compression: str = "zstd",
) -> Path:
    """Export DataFrame to Parquet format.

    Args:
        df: DataFrame to export.
        output_path: Path for the Parquet file.
        compression: Compression algorithm.

    Returns:
        Path to the exported file.
    """
    raise NotImplementedError


def export_csv(df: pl.DataFrame, output_path: Path | None = None) -> Path:
    """Export DataFrame to CSV format.

    Args:
        df: DataFrame to export.
        output_path: Path for the CSV file.

    Returns:
        Path to the exported file.
    """
    raise NotImplementedError


def export_for_tableau(df: pl.DataFrame, output_path: Path | None = None) -> Path:
    """Export DataFrame optimized for Tableau ingestion.

    Args:
        df: DataFrame to export.
        output_path: Path for the CSV file.

    Returns:
        Path to the exported file.
    """
    raise NotImplementedError


def export_for_powerbi(df: pl.DataFrame, output_path: Path | None = None) -> Path:
    """Export DataFrame optimized for Power BI ingestion.

    Args:
        df: DataFrame to export.
        output_path: Path for the CSV file.

    Returns:
        Path to the exported file.
    """
    raise NotImplementedError


def export_all(df: pl.DataFrame) -> dict[str, Path]:
    """Export dataset in all configured formats.

    Args:
        df: Final combined DataFrame.

    Returns:
        Dictionary mapping format name to output file path.
    """
    raise NotImplementedError


if __name__ == "__main__":
    print(f"IPEDS Exporter: output directory {PROCESSED_DIR}")
    print("Not yet implemented -- run after validation phase.")
