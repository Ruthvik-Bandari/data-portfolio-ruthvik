# College Scorecard Student Outcome Analytics

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-2.1+-green)
![SHAP](https://img.shields.io/badge/SHAP-Explainability-orange)

Predictive modeling pipeline that identifies which institutional factors most strongly predict **post-graduation earnings**, using the U.S. Department of Education's College Scorecard dataset (~7,000 institutions, 3,000+ variables).

## Architecture

```mermaid
flowchart TD
    Raw["College Scorecard CSV<br/>7,000+ institutions x 3,000+ vars"] --> Ingest["1. Ingest<br/>Load + handle PrivacySuppressed"]
    Ingest --> Features["2. Feature Engineering<br/>Selectivity, diversity, cost burden"]
    Features --> Train["3. Model Training<br/>Ridge / Random Forest / XGBoost"]
    Train --> SHAP["4. SHAP Analysis<br/>Feature importance + explanations"]
    Train --> Export["5. Export<br/>Parquet + Tableau CSV"]
    SHAP --> Viz["6. Visualizations<br/>4 Plotly charts + SHAP plots"]
```

## Quick Start

```bash
cd 02-college-scorecard-analytics
make setup
# Place College Scorecard CSV in data/raw/
make all
```

## License

MIT
