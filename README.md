# Data Science & Visualization Portfolio

**Ruthvik Bandari** — MS in Applied AI, Northeastern University (4.0 GPA)

A collection of end to end data science projects focused on higher education analytics. Each project demonstrates a different facet of the data lifecycle: pipeline engineering, predictive modeling, NLP, and interactive visualization — all built with production grade tooling and applied to real world education datasets.

---

## Projects

| # | Project | What It Demonstrates | Key Tech | Status |
|---|---------|---------------------|----------|--------|
| 1 | [**IPEDS Pipeline & Dashboard**](./01-ipeds-pipeline-dashboard/) | Schema harmonization across 72+ CSVs, data profiling, interactive dashboards | Polars, Pandera, Tableau, Power BI, Plotly | 🔧 In Progress |
| 2 | [**College Scorecard Analytics**](./02-college-scorecard-analytics/) | Predictive modeling, feature engineering, SHAP explainability | XGBoost, SHAP, MLflow, Tableau | ⏳ Planned |
| 3 | [**Higher Ed Text Analytics**](./03-higher-ed-text-analytics/) | NLP pipeline, topic modeling, sentiment analysis on policy documents | BERTopic, spaCy, sentence-transformers, Tableau | ⏳ Planned |
| 4 | [**Course Sentiment Dashboard**](./04-course-sentiment-dashboard/) | Aspect level sentiment extraction, DuckDB analytics, BI dashboards | spaCy, SetFit, DuckDB, Tableau, Power BI | ⏳ Planned |
| — | [**Portfolio Site**](./portfolio-site/) | Showcase site with embedded Tableau dashboards | Next.js 15, TypeScript, Tailwind CSS v4 | ⏳ Planned |

---

## Shared Standards

Every project in this portfolio follows consistent engineering practices:

**Data Processing** — Polars for all DataFrame operations. Parquet for intermediate storage. DuckDB for analytical queries.

**Visualization** — Tableau Public dashboards (interactive, embeddable), Power BI dashboards (.pbix), and Plotly for Python based interactive charts. All projects share a consistent color palette (`#2E75B6`, `#17A2B8`, `#F39C12`, `#E74C3C`, `#2ECC71`).

**Code Quality** — Type hints on every function. Docstrings on every public API. Ruff for linting and formatting. Pytest for testing. GitHub Actions CI on every push.

**Reproducibility** — uv for deterministic Python dependency management. Makefile targets for every pipeline stage. Raw data is gitignored with download instructions provided.

---

## Tech Stack

| Category | Technologies |
|----------|-------------|
| Languages | Python 3.12+, TypeScript |
| Data Processing | Polars, DuckDB, PyArrow |
| ML / NLP | scikit-learn, XGBoost, SHAP, BERTopic, spaCy, sentence-transformers |
| Visualization | Tableau Public, Power BI, Plotly, Seaborn |
| Validation | Pandera (Polars backend) |
| Infrastructure | uv, Bun, GitHub Actions, Make |
| Portfolio Site | Next.js 15, Tailwind CSS v4, Framer Motion |

---

## Quick Start

Each project is self contained. To get started with any project:

```bash
cd 01-ipeds-pipeline-dashboard/   # or any project directory
make setup                        # install dependencies via uv
make test                         # run tests
make lint                         # check code quality
```

See each project's README for dataset download instructions and full pipeline usage.

---

## About

This portfolio was built for the Research Assistant position at **Northeastern University's Center for the Future of Higher Education** under **Professor Jessica Liebowitz**, and is designed to demonstrate practical skills in data visualization, data science, and text analytics applied to higher education research.

## License

MIT
