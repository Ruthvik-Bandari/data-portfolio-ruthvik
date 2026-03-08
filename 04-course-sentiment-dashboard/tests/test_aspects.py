"""Tests for aspect extraction."""

from __future__ import annotations

import polars as pl

from src.aspects import extract_aspects


class TestExtractAspects:
    def test_detects_teaching_aspect(self) -> None:
        df = pl.DataFrame({"review_text": ["The professor was excellent and very helpful"]})
        result = extract_aspects(df)
        assert result["has_teaching_quality"][0] is True

    def test_detects_workload_aspect(self) -> None:
        df = pl.DataFrame({"review_text": ["The homework assignments were overwhelming"]})
        result = extract_aspects(df)
        assert result["has_workload"][0] is True

    def test_no_aspect_match(self) -> None:
        df = pl.DataFrame({"review_text": ["This is a generic statement about nothing specific"]})
        result = extract_aspects(df)
        aspect_cols = [c for c in result.columns if c.startswith("has_")]
        all_false = all(not result[c][0] for c in aspect_cols)
        assert all_false

    def test_multiple_aspects(self) -> None:
        df = pl.DataFrame(
            {"review_text": ["The professor teaching was great and grading was fair"]}
        )
        result = extract_aspects(df)
        assert result["has_teaching_quality"][0] is True
        assert result["has_grading"][0] is True
