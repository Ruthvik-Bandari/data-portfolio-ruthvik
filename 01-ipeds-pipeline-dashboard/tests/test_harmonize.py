"""Tests for the schema harmonization module."""

from __future__ import annotations

import polars as pl
import pytest

from src.harmonize import apply_column_mapping, apply_type_coercions


class TestApplyColumnMapping:
    """Tests for apply_column_mapping function."""

    @pytest.mark.skip(reason="Not yet implemented")
    def test_renames_columns_according_to_mapping(self) -> None:
        """Verify columns are renamed correctly."""
        df = pl.DataFrame({"EFRACE01": [1, 2], "UNITID": [100001, 100002]})
        mapping = {"EFRACE01": "enrollment_race", "UNITID": "unitid"}
        result = apply_column_mapping(df, mapping)
        assert result.columns == ["enrollment_race", "unitid"]

    @pytest.mark.skip(reason="Not yet implemented")
    def test_ignores_unmapped_columns(self) -> None:
        """Verify unmapped columns pass through unchanged."""
        df = pl.DataFrame({"A": [1], "B": [2], "C": [3]})
        mapping = {"A": "alpha"}
        result = apply_column_mapping(df, mapping)
        assert "alpha" in result.columns
        assert "B" in result.columns

    @pytest.mark.skip(reason="Not yet implemented")
    def test_empty_mapping_returns_unchanged(self) -> None:
        """Verify empty mapping returns original columns."""
        df = pl.DataFrame({"X": [1], "Y": [2]})
        result = apply_column_mapping(df, {})
        assert result.columns == ["X", "Y"]


class TestApplyTypeCoercions:
    """Tests for apply_type_coercions function."""

    @pytest.mark.skip(reason="Not yet implemented")
    def test_casts_string_to_int(self) -> None:
        """Verify string to integer coercion."""
        df = pl.DataFrame({"unitid": ["100001", "100002"]})
        result = apply_type_coercions(df, {"unitid": pl.Int64})
        assert result["unitid"].dtype == pl.Int64

    @pytest.mark.skip(reason="Not yet implemented")
    def test_invalid_cast_produces_nulls(self) -> None:
        """Verify invalid values become null on non strict cast."""
        df = pl.DataFrame({"enrollment": ["500", "abc", "300"]})
        result = apply_type_coercions(df, {"enrollment": pl.Int64})
        assert result["enrollment"].null_count() == 1

    @pytest.mark.skip(reason="Not yet implemented")
    def test_preserves_non_coerced_columns(self) -> None:
        """Verify columns not in coercions map stay unchanged."""
        df = pl.DataFrame({"a": [1], "b": ["hello"]})
        result = apply_type_coercions(df, {"a": pl.Float64})
        assert result["b"].dtype == pl.Utf8
