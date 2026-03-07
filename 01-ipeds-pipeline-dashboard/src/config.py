"""Configuration constants, paths, and settings for the IPEDS pipeline.

Central location for all project configuration. Import from here instead
of hardcoding paths or magic values in other modules.
"""

from __future__ import annotations

from pathlib import Path

# ── Project Paths ────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
SCHEMAS_DIR = DATA_DIR / "schemas"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_IMAGES_DIR = REPORTS_DIR / "images"
DASHBOARDS_DIR = PROJECT_ROOT / "dashboards"

# ── Survey Configuration ─────────────────────────────────────────────────────

SURVEY_YEARS: list[int] = [2018, 2019, 2020, 2021, 2022, 2023, 2024]

SURVEY_COMPONENTS: dict[str, str] = {
    "hd": "Institutional Characteristics",
    "effy": "12-Month Enrollment",
    "c": "Completions",
    "gr": "Graduation Rates",
}

# Maps component prefix to the glob pattern for its raw CSV files.
# Completions files have a `_a` suffix; others are just `{prefix}{year}.csv`.
COMPONENT_FILE_PATTERNS: dict[str, str] = {
    "hd": "hd{year}.csv",
    "effy": "effy{year}.csv",
    "c": "c{year}_a.csv",
    "gr": "gr{year}.csv",
}

PRIMARY_KEY = "UNITID"

# ── Missing Data Codes ───────────────────────────────────────────────────────

NULL_VALUES: list[str] = ["-1", "-2", ".", "", "NA", "NULL", "N/A"]

MISSING_DATA_CODES: dict[str, str] = {
    "-1": "Not reported",
    "-2": "Not applicable",
    ".": "Not available",
    "": "Missing (empty string)",
    "NULL": "Missing (explicit NULL)",
}

# ── File Encoding ────────────────────────────────────────────────────────────

ENCODING_PRIORITY: list[str] = ["utf-8", "latin-1", "cp1252"]

# ── Portfolio Visualization Theme ────────────────────────────────────────────

PORTFOLIO_COLORS: dict[str, str] = {
    "primary": "#2E75B6",
    "secondary": "#1B4F72",
    "accent": "#17A2B8",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "success": "#2ECC71",
    "text": "#2C3E50",
    "light": "#ECF0F1",
}

COLORWAY: list[str] = [
    "#2E75B6",
    "#17A2B8",
    "#F39C12",
    "#E74C3C",
    "#2ECC71",
    "#9B59B6",
    "#1ABC9C",
    "#E67E22",
]

PLOTLY_TEMPLATE: dict = {
    "layout": {
        "font": {"family": "Inter, system-ui, sans-serif", "color": PORTFOLIO_COLORS["text"]},
        "colorway": COLORWAY,
        "plot_bgcolor": "white",
        "paper_bgcolor": "white",
        "title": {"font": {"size": 20, "color": PORTFOLIO_COLORS["secondary"]}},
        "xaxis": {"gridcolor": "#E5E5E5", "linecolor": "#BDC3C7"},
        "yaxis": {"gridcolor": "#E5E5E5", "linecolor": "#BDC3C7"},
        "hoverlabel": {"bgcolor": "white", "font_size": 12},
    }
}
