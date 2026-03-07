# Data Download Instructions — IPEDS

Raw data files are **not committed to git** due to size.

## Quick Download

1. Go to **https://nces.ed.gov/ipeds/use-the-data**
2. Click **"Survey Data"** → **"Complete Data Files"**

## Required Survey Components

Download for each year **2018–2024**:

| Component | Prefix | Contains |
|-----------|--------|----------|
| Institutional Characteristics | `HD` | Name, address, sector, Carnegie classification |
| Fall Enrollment | `EF` / `EFFY` | Enrollment by race, gender, attendance |
| Completions | `C` | Degrees awarded by program, level, race |
| Graduation Rates | `GR` | Cohort graduation rates by race and gender |

Place all CSVs in this `data/raw/` directory.

## Missing Data Codes

| Code | Meaning |
|------|---------|
| `-1` | Not reported |
| `-2` | Not applicable |
| `.`  | Not available |
| Empty | Missing |

The pipeline maps all of these to Polars null values.
