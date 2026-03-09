# Data Science & Visualization Portfolio

**Ruthvik Nath Bandari** — MS in Applied AI, Northeastern University (4.0 GPA)

A collection of end to end data science projects demonstrating pipeline engineering, predictive modeling, NLP, and interactive visualization — all built with production grade tooling and applied to real world education datasets.

---

## Projects

| # | Project | What It Demonstrates | Key Tech |
|---|---------|---------------------|----------|
| 1 | [**IPEDS Pipeline & Dashboard**](./01-ipeds-pipeline-dashboard/) | Schema harmonization across 72+ CSVs, 3M+ rows processed, interactive dashboards | Polars, Pandera, Plotly, Tableau |
| 2 | [**College Scorecard Analytics**](./02-college-scorecard-analytics/) | Predictive modeling (R²=0.934), feature engineering, SHAP explainability | XGBoost, SHAP, scikit-learn, Plotly |
| 3 | [**Higher Ed Text Analytics**](./03-higher-ed-text-analytics/) | NLP pipeline, BERTopic topic modeling, sentiment analysis on research abstracts | BERTopic, Transformers, KeyBERT, Plotly |
| 4 | [**Course Sentiment Dashboard**](./04-course-sentiment-dashboard/) | Aspect level sentiment extraction across 5,000 reviews, DuckDB analytics | Transformers, DuckDB, Polars, Plotly |

---

## Tableau Dashboards

All projects include published, interactive Tableau dashboards:

| Project | Dashboard | Highlights |
|---------|-----------|------------|
| IPEDS Pipeline | [View Dashboard](https://public.tableau.com/app/profile/ruthvik.nath.bandari/viz/IPEDSHigherEducationDashboard/Dashboard1) | Institution trends by sector, geographic map, enrollment & completions |
| College Scorecard | [View Dashboard](https://public.tableau.com/app/profile/ruthvik.nath.bandari/viz/CollegeScorecardAnalytics_/Dashboard1) | Cost vs earnings scatter, state map, selectivity analysis, earnings distribution |
| Text Analytics | [View Dashboard](https://public.tableau.com/app/profile/ruthvik.nath.bandari/viz/HigherEducationTextAnalytics/HigherEducationTextAnalytics) | Topic distribution, sentiment timeline, topic x year heatmap |
| Course Sentiment | [View Dashboard](https://public.tableau.com/app/profile/ruthvik.nath.bandari/viz/CourseSentimentDashboard/CourseReviewSentimentDashboard) | Department sentiment, aspect heatmap, temporal trends, rating alignment |

---

## Portfolio at a Glance

| Metric | Value |
|--------|-------|
| Total rows processed | **3,055,192** |
| Published Tableau dashboards | **4** |
| Plotly visualizations | **22** |
| Tests passing | **47** |
| Best model R² | **0.934** |

---

## Shared Standards

Every project in this portfolio follows consistent engineering practices:

**Data Processing** — Polars for all DataFrame operations. Parquet for intermediate storage. DuckDB for analytical queries.

**Visualization** — Tableau Public dashboards (interactive, embeddable) and Plotly for Python based interactive charts. All projects share a consistent color palette (`#2E75B6`, `#17A2B8`, `#F39C12`, `#E74C3C`, `#2ECC71`).

**Code Quality** — Type hints on every function. Docstrings on every public API. Ruff for linting and formatting. Pytest for testing. GitHub Actions CI on every push.

**Reproducibility** — uv for deterministic Python dependency management. Makefile targets for every pipeline stage. Raw data is gitignored with download instructions provided.

---

## Tech Stack

| Category | Technologies |
|----------|-------------|
| Languages | Python 3.12+, TypeScript |
| Data Processing | Polars, DuckDB, PyArrow |
| ML / NLP | scikit-learn, XGBoost, SHAP, BERTopic, Transformers, KeyBERT |
| Visualization | Tableau Public, Plotly, Seaborn |
| Validation | Pandera (Polars backend) |
| Infrastructure | uv, GitHub Actions, Make, pytest, ruff |
| Portfolio Site | React 19, Tailwind CSS, Framer Motion |

---

## Quick Start

Each project is self contained:

```bash
cd 01-ipeds-pipeline-dashboard/   # or any project directory
make setup                        # install dependencies via uv
make all                          # run full pipeline
make test                         # run tests
make lint                         # check code quality
```

See each project's README for dataset download instructions and full pipeline usage.

---

## License

MIT
