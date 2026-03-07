# Higher Education Policy Text Analytics

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![BERTopic](https://img.shields.io/badge/BERTopic-Topic_Modeling-green)
![SHAP](https://img.shields.io/badge/Transformers-Sentiment-orange)

NLP pipeline for topic modeling, sentiment analysis, and keyword extraction on higher education research documents from the ERIC database (~500+ abstracts, 2018-2024).

## Architecture

```mermaid
flowchart TD
    ERIC["ERIC Database API<br/>500+ research abstracts"] --> Collect["1. Collect<br/>Search + download"]
    Collect --> Preprocess["2. Preprocess<br/>Clean + tokenize"]
    Preprocess --> Topics["3. BERTopic<br/>Topic modeling"]
    Topics --> Sentiment["4. Sentiment<br/>DistilBERT classifier"]
    Sentiment --> Keywords["5. KeyBERT<br/>Keyword extraction"]
    Keywords --> Viz["6. Visualize<br/>4 Plotly charts"]
    Keywords --> Export["7. Export<br/>Tableau CSV"]
```

## Quick Start

```bash
cd 03-higher-ed-text-analytics
make setup
make all
```

## Key Outputs
- BERTopic model with 15-25 interpretable topics
- Sentiment trends across publication years
- Topic prevalence heatmap over time
- Keyword extraction per document
- Tableau ready CSV export

## License

MIT
