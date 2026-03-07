"""Tests for the schema harmonization module."""

from __future__ import annotations

import polars as pl

from src.harmonize import (
    apply_column_mapping,
    apply_type_coercions,
    build_type_coercions,
    normalize_columns,
)


class TestNormalizeColumns:
    """Tests for normalize_columns function."""

    def test_strips_whitespace_from_column_names(self) -> None:
        """Verify trailing whitespace is removed (e.g., 'EFYGUKN ' bug)."""
        df = pl.DataFrame({"GOOD": [1], "BAD ": [2], " ALSO_BAD ": [3]})
        result = normalize_columns(df)
        assert result.columns == ["GOOD", "BAD", "ALSO_BAD"]

    def test_uppercases_column_names(self) -> None:
        """Verify column names are uppercased."""
        df = pl.DataFrame({"lower": [1], "MiXeD": [2]})
        result = normalize_columns(df)
        assert result.columns == ["LOWER", "MIXED"]

    def test_preserves_data(self) -> None:
        """Verify data is not changed by normalization."""
        df = pl.DataFrame({"col_a ": [1, 2, 3]})
        result = normalize_columns(df)
        assert result["COL_A"].to_list() == [1, 2, 3]


class TestApplyColumnMapping:
    """Tests for apply_column_mapping function."""

    def test_renames_columns_according_to_mapping(self) -> None:
        """Verify columns are renamed correctly."""
        df = pl.DataFrame({"EFRACE01": [1, 2], "UNITID": [100001, 100002]})
        mapping = {"EFRACE01": "ENROLLMENT_RACE", "UNITID": "INSTITUTION_ID"}
        result = apply_column_mapping(df, mapping)
        assert result.columns == ["ENROLLMENT_RACE", "INSTITUTION_ID"]

    def test_ignores_unmapped_columns(self) -> None:
        """Verify unmapped columns pass through unchanged."""
        df = pl.DataFrame({"A": [1], "B": [2], "C": [3]})
        mapping = {"A": "ALPHA"}
        result = apply_column_mapping(df, mapping)
        assert "ALPHA" in result.columns
        assert "B" in result.columns
        assert "C" in result.columns

    def test_empty_mapping_returns_unchanged(self) -> None:
        """Verify empty mapping returns original columns."""
        df = pl.DataFrame({"X": [1], "Y": [2]})
        result = apply_column_mapping(df, {})
        assert result.columns == ["X", "Y"]

    def test_ignores_mapping_keys_not_in_dataframe(self) -> None:
        """Verify mapping keys for nonexistent columns are ignored."""
        df = pl.DataFrame({"A": [1]})
        mapping = {"A": "ALPHA", "NONEXISTENT": "GONE"}
        result = apply_column_mapping(df, mapping)
        assert result.columns == ["ALPHA"]


class TestApplyTypeCoercions:
    """Tests for apply_type_coercions function."""

    def test_casts_string_to_int(self) -> None:
        """Verify string to integer coercion."""
        df = pl.DataFrame({"UNITID": ["100001", "100002"]})
        result = apply_type_coercions(df, {"UNITID": pl.Int64})
        assert result["UNITID"].dtype == pl.Int64
        assert result["UNITID"].to_list() == [100001, 100002]

    def test_invalid_cast_produces_nulls(self) -> None:
        """Verify invalid values become null on non strict cast."""
        df = pl.DataFrame({"ENROLLMENT": ["500", "abc", "300"]})
        result = apply_type_coercions(df, {"ENROLLMENT": pl.Int64})
        assert result["ENROLLMENT"].null_count() == 1
        assert result["ENROLLMENT"][0] == 500
        assert result["ENROLLMENT"][2] == 300

    def test_preserves_non_coerced_columns(self) -> None:
        """Verify columns not in coercions map stay unchanged."""
        df = pl.DataFrame({"A": [1], "B": ["hello"]})
        result = apply_type_coercions(df, {"A": pl.Float64})
        assert result["B"].dtype == pl.String

    def test_skips_already_correct_type(self) -> None:
        """Verify no change when column already has target type."""
        df = pl.DataFrame({"X": pl.Series([1, 2, 3], dtype=pl.Int64)})
        result = apply_type_coercions(df, {"X": pl.Int64})
        assert result["X"].dtype == pl.Int64
        assert result["X"].to_list() == [1, 2, 3]


class TestBuildTypeCoercions:
    """Tests for build_type_coercions function."""

    def test_detects_mixed_int_string(self) -> None:
        """Verify Int64/String mix is resolved to Int64."""
        dfs = {
            2020: pl.DataFrame({"COL": pl.Series([1, 2], dtype=pl.Int64)}),
            2021: pl.DataFrame({"COL": pl.Series(["3", "4"], dtype=pl.String)}),
        }
        coercions = build_type_coercions(dfs)
        assert "COL" in coercions
        assert coercions["COL"] == pl.Int64

    def test_consistent_types_produce_no_coercions(self) -> None:
        """Verify no coercions when all years have same types."""
        dfs = {
            2020: pl.DataFrame({"A": [1], "B": ["x"]}),
            2021: pl.DataFrame({"A": [2], "B": ["y"]}),
        }
        coercions = build_type_coercions(dfs)
        assert len(coercions) == 0

    def test_float_wins_over_int(self) -> None:
        """Verify Float64 is chosen when mixed with Int64."""
        dfs = {
            2020: pl.DataFrame({"RATE": pl.Series([1.5], dtype=pl.Float64)}),
            2021: pl.DataFrame({"RATE": pl.Series([2], dtype=pl.Int64)}),
        }
        coercions = build_type_coercions(dfs)
        assert coercions.get("RATE") == pl.Float64
