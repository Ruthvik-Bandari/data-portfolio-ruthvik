"""Tests for feature engineering module."""

from __future__ import annotations

import polars as pl

from src.features import engineer_features, numeric_cast


class TestNumericCast:
    """Tests for numeric_cast function."""

    def test_casts_string_to_float(self) -> None:
        """Verify string numbers are cast to Float64."""
        df = pl.DataFrame({"ADM_RATE": ["0.5", "0.8"]})
        result = numeric_cast(df, ["ADM_RATE"])
        assert result["ADM_RATE"].dtype == pl.Float64

    def test_handles_privacy_suppressed(self) -> None:
        """Verify null values from PrivacySuppressed are handled."""
        df = pl.DataFrame({"SAT_AVG": [None, "1200", None]})
        result = numeric_cast(df, ["SAT_AVG"])
        assert result["SAT_AVG"].null_count() == 2

    def test_ignores_missing_columns(self) -> None:
        """Verify nonexistent columns are silently skipped."""
        df = pl.DataFrame({"A": [1.0]})
        result = numeric_cast(df, ["A", "NONEXISTENT"])
        assert result.columns == ["A"]


class TestEngineerFeatures:
    """Tests for engineer_features function."""

    def test_creates_selectivity_index(self) -> None:
        """Verify selectivity index is computed."""
        df = pl.DataFrame({"ADM_RATE": [0.5, 0.8], "SAT_AVG": [1200.0, 1000.0]})
        result = engineer_features(df)
        assert "SELECTIVITY_INDEX" in result.columns
        assert result["SELECTIVITY_INDEX"][0] == 600.0

    def test_creates_diversity_index(self) -> None:
        """Verify diversity index is computed from demographic shares."""
        df = pl.DataFrame(
            {
                "UGDS_WHITE": [0.5],
                "UGDS_BLACK": [0.2],
                "UGDS_HISP": [0.15],
                "UGDS_ASIAN": [0.1],
                "UGDS_AIAN": [0.01],
                "UGDS_NHPI": [0.01],
                "UGDS_2MOR": [0.02],
                "UGDS_NRA": [0.005],
                "UGDS_UNKN": [0.005],
            }
        )
        result = engineer_features(df)
        assert "DIVERSITY_INDEX" in result.columns
        assert result["DIVERSITY_INDEX"][0] > 0  # Should be positive for diverse inst

    def test_creates_size_category(self) -> None:
        """Verify size categories are assigned."""
        df = pl.DataFrame({"UGDS": [500.0, 3000.0, 10000.0, 30000.0]})
        result = engineer_features(df)
        assert "SIZE_CATEGORY" in result.columns
        assert result["SIZE_CATEGORY"].to_list() == ["Small", "Medium", "Large", "Very Large"]
