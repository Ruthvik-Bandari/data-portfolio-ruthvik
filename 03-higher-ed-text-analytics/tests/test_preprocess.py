"""Tests for text preprocessing."""

from __future__ import annotations

from src.preprocess import clean_text


class TestCleanText:
    """Tests for clean_text function."""

    def test_removes_extra_whitespace(self) -> None:
        result = clean_text("hello   world\n\tnew")
        assert "  " not in result

    def test_strips_leading_trailing(self) -> None:
        result = clean_text("  hello  ")
        assert result == "hello"

    def test_handles_empty_string(self) -> None:
        assert clean_text("") == ""

    def test_handles_none(self) -> None:
        assert clean_text(None) == ""

    def test_preserves_normal_punctuation(self) -> None:
        result = clean_text("Hello, world! How's it going?")
        assert "," in result
        assert "!" in result
