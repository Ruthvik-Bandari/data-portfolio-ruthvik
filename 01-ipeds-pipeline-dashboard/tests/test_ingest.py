"""Tests for the data ingestion module."""

from __future__ import annotations

from src.ingest import parse_filename


class TestParseFilename:
    """Tests for parse_filename function."""

    def test_parses_hd_file(self) -> None:
        """Verify HD filename parsing."""
        result = parse_filename("hd2018.csv")
        assert result == ("hd", 2018)

    def test_parses_effy_file(self) -> None:
        """Verify EFFY filename parsing."""
        result = parse_filename("effy2022.csv")
        assert result == ("effy", 2022)

    def test_parses_completions_file(self) -> None:
        """Verify Completions (C_A) filename parsing."""
        result = parse_filename("c2020_a.csv")
        assert result == ("c", 2020)

    def test_parses_graduation_rates_file(self) -> None:
        """Verify GR filename parsing."""
        result = parse_filename("gr2024.csv")
        assert result == ("gr", 2024)

    def test_rejects_unknown_prefix(self) -> None:
        """Verify unknown prefixes return None."""
        assert parse_filename("xyz2020.csv") is None

    def test_rejects_rv_files(self) -> None:
        """Verify revised value files are not matched."""
        assert parse_filename("hd2018_rv.csv") is None

    def test_handles_uppercase(self) -> None:
        """Verify case insensitive matching."""
        result = parse_filename("HD2019.csv")
        assert result == ("hd", 2019)

    def test_rejects_non_csv(self) -> None:
        """Verify non-CSV files return None."""
        assert parse_filename("hd2018.xlsx") is None
