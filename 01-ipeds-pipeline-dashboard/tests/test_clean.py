"""Tests for the data cleaning module."""

from __future__ import annotations

import polars as pl
import pytest

from src.clean import clean_string_columns, deduplicate_institutions, standardize_nulls


class TestStandardizeNulls:
    """Tests for standardize_nulls function."""

    @pytest.mark.skip(reason="Not yet implemented")
    def test_replaces_negative_one_with_null(self) -> None:
        """Verify -1 (not reported) is converted to null."""
        df = pl.DataFrame({"value": ["-1", "500", "300"]})
        result = standardize_nulls(df)
        assert result["value"].null_count() >= 1

    @pytest.mark.skip(reason="Not yet implemented")
    def test_replaces_dot_with_null(self) -> None:
        """Verify dot is converted to null."""
        df = pl.DataFrame({"value": [".", "100", "200"]})
        result = standardize_nulls(df)
        assert result["value"].null_count() >= 1

    @pytest.mark.skip(reason="Not yet implemented")
    def test_preserves_valid_values(self) -> None:
        """Verify valid values are not altered."""
        df = pl.DataFrame({"value": ["100", "200", "300"]})
        result = standardize_nulls(df)
        assert result["value"].null_count() == 0


class TestDeduplicateInstitutions:
    """Tests for deduplicate_institutions function."""

    @pytest.mark.skip(reason="Not yet implemented")
    def test_removes_duplicate_unitids(self) -> None:
        """Verify duplicate UNITID rows are removed."""
        df = pl.DataFrame({
            "UNITID": [100001, 100001, 100002],
            "name": ["MIT", "MIT (dup)", "Harvard"],
        })
        result = deduplicate_institutions(df)
        assert result.height == 2

    @pytest.mark.skip(reason="Not yet implemented")
    def test_no_duplicates_returns_same(self) -> None:
        """Verify no change when no duplicates exist."""
        df = pl.DataFrame({"UNITID": [100001, 100002, 100003]})
        result = deduplicate_institutions(df)
        assert result.height == 3


class TestCleanStringColumns:
    """Tests for clean_string_columns function."""

    @pytest.mark.skip(reason="Not yet implemented")
    def test_strips_whitespace(self) -> None:
        """Verify leading/trailing whitespace is removed."""
        df = pl.DataFrame({"name": ["  MIT  ", " Harvard "]})
        result = clean_string_columns(df)
        assert result["name"].to_list() == ["MIT", "Harvard"]

    @pytest.mark.skip(reason="Not yet implemented")
    def test_preserves_numeric_columns(self) -> None:
        """Verify numeric columns are not affected."""
        df = pl.DataFrame({"id": [1, 2], "name": ["a", "b"]})
        result = clean_string_columns(df)
        assert result["id"].dtype == pl.Int64
