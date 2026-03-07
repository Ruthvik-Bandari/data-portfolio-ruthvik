"""Data combination module for IPEDS datasets.

Joins survey components on UNITID within each year, then stacks
multi year data with a survey_year column.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl

from src.config import PRIMARY_KEY

if TYPE_CHECKING:
    pass


def join_components_for_year(
    components: dict[str, pl.DataFrame], year: int, join_key: str = PRIMARY_KEY,
) -> pl.DataFrame:
    """Join multiple survey components for a single year.

    Args:
        components: Dictionary mapping component prefix to DataFrame.
        year: The survey year (added as a column).
        join_key: Column to join on. Defaults to UNITID.

    Returns:
        Combined DataFrame with all components joined.
    """
    raise NotImplementedError


def stack_years(yearly_frames: dict[int, pl.DataFrame]) -> pl.DataFrame:
    """Stack multiple years of combined data vertically.

    Args:
        yearly_frames: Dictionary mapping year to combined DataFrame.

    Returns:
        Single DataFrame with all years stacked.
    """
    raise NotImplementedError


def combine_all(
    cleaned_data: dict[str, dict[int, pl.DataFrame]],
) -> pl.DataFrame:
    """Run the full combination pipeline.

    Args:
        cleaned_data: Nested dictionary of component -> year -> DataFrame.

    Returns:
        Final combined and stacked DataFrame.
    """
    raise NotImplementedError


if __name__ == "__main__":
    print(f"IPEDS Combiner: joining on {PRIMARY_KEY}")
    print("Not yet implemented -- run after cleaning phase.")
