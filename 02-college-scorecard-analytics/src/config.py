"""Configuration for the College Scorecard analytics pipeline."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FEATURES_DIR = DATA_DIR / "features"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_IMAGES_DIR = REPORTS_DIR / "images"

# Target variable: median earnings 10 years after enrollment
TARGET = "MD_EARN_WNE_P10"

# Key feature groups from College Scorecard
ADMISSIONS_COLS = [
    "ADM_RATE",
    "ADM_RATE_ALL",
    "SATVRMID",
    "SATMTMID",
    "SATWRMID",
    "ACTCMMID",
    "ACTENMID",
    "ACTMTMID",
    "ACTWRMID",
    "SAT_AVG",
    "SAT_AVG_ALL",
]

COST_COLS = [
    "COSTT4_A",
    "COSTT4_P",
    "TUITIONFEE_IN",
    "TUITIONFEE_OUT",
    "TUITIONFEE_PROG",
    "TUITFTE",
    "INEXPFTE",
    "AVGFACSAL",
    "NPT4_PUB",
    "NPT4_PRIV",
    "NPT4_PROG",
    "NPT4_OTHER",
    "NUM4_PUB",
    "NUM4_PRIV",
]

OUTCOME_COLS = [
    "MD_EARN_WNE_P10",
    "MD_EARN_WNE_P8",
    "MD_EARN_WNE_P6",
    "GT_25K_P10",
    "GT_25K_P6",
    "MN_EARN_WNE_P10",
    "MN_EARN_WNE_P8",
    "GRAD_DEBT_MDN",
    "GRAD_DEBT_MDN10YR",
    "RPY_3YR_RT",
]

COMPLETION_COLS = [
    "C150_4",
    "C150_L4",
    "C200_4",
    "C200_L4",
    "RET_FT4",
    "RET_FTL4",
    "RET_PT4",
    "RET_PTL4",
    "PCTFLOAN",
    "PCTPELL",
    "UG25ABV",
]

DEMOGRAPHIC_COLS = [
    "UGDS",
    "UGDS_WHITE",
    "UGDS_BLACK",
    "UGDS_HISP",
    "UGDS_ASIAN",
    "UGDS_AIAN",
    "UGDS_NHPI",
    "UGDS_2MOR",
    "UGDS_NRA",
    "UGDS_UNKN",
    "UGDS_MEN",
    "UGDS_WOMEN",
]

INSTITUTION_COLS = [
    "UNITID",
    "INSTNM",
    "STABBR",
    "CONTROL",
    "PREDDEG",
    "HIGHDEG",
    "REGION",
    "LOCALE",
    "CCBASIC",
    "CCUGPROF",
    "CCSIZSET",
    "HBCU",
    "PBI",
    "ANNHI",
    "TRIBAL",
    "AANAPII",
    "HSI",
    "NANTI",
    "MENONLY",
    "WOMENONLY",
    "DISTANCEONLY",
    "CURROPER",
]

# Null sentinels in College Scorecard
NULL_VALUES = ["PrivacySuppressed", "NULL", ""]

# Portfolio colors (consistent with P1)
PORTFOLIO_COLORS = {
    "primary": "#2E75B6",
    "secondary": "#1B4F72",
    "accent": "#17A2B8",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "success": "#2ECC71",
    "text": "#2C3E50",
    "light": "#ECF0F1",
}

COLORWAY = [
    "#2E75B6",
    "#17A2B8",
    "#F39C12",
    "#E74C3C",
    "#2ECC71",
    "#9B59B6",
    "#1ABC9C",
    "#E67E22",
]
