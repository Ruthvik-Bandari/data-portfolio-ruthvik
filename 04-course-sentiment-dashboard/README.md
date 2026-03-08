# Course Review Sentiment Dashboard

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-Analytics-green)
![Transformers](https://img.shields.io/badge/Transformers-Sentiment-orange)

Aspect level sentiment analysis pipeline for higher education course reviews. Extracts sentiments for specific aspects (teaching quality, workload, grading, engagement) and aggregates results with DuckDB for interactive dashboards.

## Architecture

```mermaid
flowchart TD
    Data["5,000 Course Reviews<br/>(12 departments, 2020-2024)"] --> Aspects["1. Aspect Extraction<br/>6 categories via keyword matching"]
    Aspects --> Sentiment["2. Sentiment Analysis<br/>DistilBERT per review"]
    Sentiment --> DuckDB["3. DuckDB Aggregation<br/>Dept x Aspect x Time"]
    DuckDB --> Viz["4. Visualizations<br/>4 Plotly charts"]
    DuckDB --> Export["5. Export<br/>Tableau CSV"]
```

## Quick Start

```bash
cd 04-course-sentiment-dashboard
make setup
make all
```

## Key Outputs
- Aspect level sentiment (teaching, content, workload, grading, accessibility, engagement)
- Department x Aspect heatmap
- Temporal sentiment trends
- Rating vs sentiment alignment analysis

## License

MIT
