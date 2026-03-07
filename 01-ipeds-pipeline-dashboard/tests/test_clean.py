"""Tests for the data cleaning module."""

from __future__ import annotations

import polars as pl

from src.clean import clean_string_columns, deduplicate_institutions, process_imputation_flags


class TestDeduplicateInstitutions:
    """Tests for deduplicate_institutions function."""

    def test_removes_exact_duplicate_rows(self) -> None:
        """Verify exact duplicate rows are removed."""
        df = pl.DataFrame(
            {
                "UNITID": [100001, 100001, 100002],
                "NAME": ["MIT", "MIT", "Harvard"],
                "VALUE": [10, 10, 20],
            }
        )
        result = deduplicate_institutions(df)
        assert result.height == 2

    def test_keeps_different_rows_same_unitid(self) -> None:
        """Multi-row components (Completions) have same UNITID but different data."""
        df = pl.DataFrame(
            {
                "UNITID": [100001, 100001, 100002],
                "NAME": ["MIT", "MIT", "Harvard"],
                "PROGRAM": ["CS", "Math", "Law"],
            }
        )
        result = deduplicate_institutions(df)
        assert result.height == 3  # All rows are unique

    def test_no_duplicates_returns_same_count(self) -> None:
        """Verify no change when no duplicates exist."""
        df = pl.DataFrame({"UNITID": [100001, 100002, 100003]})
        result = deduplicate_institutions(df)
        assert result.height == 3

    def test_handles_missing_key_column(self) -> None:
        """Verify graceful handling when UNITID column is absent."""
        df = pl.DataFrame({"OTHER": [1, 2, 3]})
        result = deduplicate_institutions(df)
        assert result.height == 3


class TestCleanStringColumns:
    """Tests for clean_string_columns function."""

    def test_strips_whitespace(self) -> None:
        """Verify leading/trailing whitespace is removed."""
        df = pl.DataFrame({"NAME": ["  MIT  ", " Harvard "]})
        result = clean_string_columns(df)
        assert result["NAME"].to_list() == ["MIT", "Harvard"]

    def test_preserves_numeric_columns(self) -> None:
        """Verify numeric columns are not affected."""
        df = pl.DataFrame({"ID": [1, 2], "NAME": ["a", "b"]})
        result = clean_string_columns(df)
        assert result["ID"].dtype == pl.Int64
        assert result["ID"].to_list() == [1, 2]

    def test_handles_no_string_columns(self) -> None:
        """Verify no error when DataFrame has no string columns."""
        df = pl.DataFrame({"A": [1, 2], "B": [3.0, 4.0]})
        result = clean_string_columns(df)
        assert result.height == 2


class TestProcessImputationFlags:
    """Tests for process_imputation_flags function."""

    def test_casts_numeric_flag_to_string(self) -> None:
        """IPEDS imputation flags (X columns) should be String type."""
        df = pl.DataFrame(
            {
                "VALUE": [100, 200],
                "XVALUE": pl.Series([1, 0], dtype=pl.Int64),
            }
        )
        result = process_imputation_flags(df)
        assert result["XVALUE"].dtype == pl.String

    def test_preserves_string_flags(self) -> None:
        """Flags already as String should stay unchanged."""
        df = pl.DataFrame(
            {
                "VALUE": [100, 200],
                "XVALUE": ["A", "B"],
            }
        )
        result = process_imputation_flags(df)
        assert result["XVALUE"].dtype == pl.String
        assert result["XVALUE"].to_list() == ["A", "B"]

    def test_no_flag_columns_returns_unchanged(self) -> None:
        """Verify no error when no X-prefixed columns exist."""
        df = pl.DataFrame({"A": [1], "B": [2]})
        result = process_imputation_flags(df)
        assert result.columns == ["A", "B"]
