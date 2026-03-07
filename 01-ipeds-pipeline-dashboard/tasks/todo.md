# IPEDS Higher Education Data Pipeline & Dashboard — Task Tracker

## Current Sprint: Phase 1 — Data Profiling

### 1.1 Data Acquisition
- [ ] Download IPEDS Complete Data Files for 2018–2024 (6 academic years)
- [ ] Download Institutional Characteristics (HD) survey for each year
- [ ] Download Fall Enrollment (EF) survey for each year
- [ ] Download Completions (C) survey for each year
- [ ] Download Graduation Rates (GR) survey for each year
- [ ] Download corresponding data dictionaries for each survey component
- [ ] Place all raw CSVs in `data/raw/`
- [ ] Verify file counts: expect ~24 CSVs (4 components × 6 years)

### 1.2 Data Profiling Pipeline
- [ ] Implement `src/ingest.py` — read all raw CSVs into Polars DataFrames
  - [ ] Handle encoding issues (some IPEDS files use Latin-1)
  - [ ] Detect and log file sizes, row counts, column counts per file
- [ ] Implement `src/profile.py` — automated schema detection
  - [ ] For each CSV: detect column data types via `infer_schema_length`
  - [ ] Compute null rate per column per file
  - [ ] Compute value distributions for categorical columns
  - [ ] Identify columns that change names across years
  - [ ] Output profiling results as structured Polars DataFrames

### 1.3 Schema Comparison Report
- [ ] Generate cross year schema comparison matrix
- [ ] Identify column name changes (e.g., `EFRACE01` → `EFRACE15`)
- [ ] Document data type inconsistencies
- [ ] Document missing data coding differences
- [ ] Write `reports/schema_mapping.md`

### 1.4 Notebooks
- [ ] Complete `notebooks/01_data_exploration.ipynb` with initial EDA
- [ ] Complete `notebooks/02_schema_analysis.ipynb` with cross year comparison visuals

### 1.5 Validation & Testing
- [ ] Write tests for `ingest.py`
- [ ] Write tests for `profile.py`
- [ ] All tests passing via `make test`
- [ ] Lint clean via `make lint`

### 1.6 Documentation
- [ ] Update README.md with Phase 1 findings
- [ ] Generate `reports/data_quality_report.html`

---

## Upcoming Phases
- **Phase 2:** Schema Harmonization
- **Phase 3:** Clean + Combine
- **Phase 4:** Visualizations (Tableau, Power BI, Plotly)

## Completed
- [x] Project scaffold created (2026-03-07)

## Review Notes
- IPEDS data URL: https://nces.ed.gov/ipeds/use-the-data → Complete Data Files
- UNITID is the primary key across all survey components
