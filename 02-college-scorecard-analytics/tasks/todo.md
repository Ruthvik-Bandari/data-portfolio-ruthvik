# College Scorecard Analytics — Task Tracker

## Current Sprint: Phase 1 — EDA + Feature Engineering

### 1.1 Data Acquisition
- [ ] Download Most Recent Institution-Level Data from collegescorecard.ed.gov/data
- [ ] Place CSV in data/raw/
- [ ] Verify: ~7,000 institutions x 3,000+ variables

### 1.2 EDA
- [ ] Load data with Polars, profile columns
- [ ] Identify target: MD_EARN_WNE_P10 (median earnings 10 years post enrollment)
- [ ] Analyze missing data patterns (many columns >50% null)
- [ ] Document key variable groups: admissions, cost, demographics, outcomes

### 1.3 Feature Engineering
- [ ] Selectivity index: admission rate x SAT average
- [ ] Cost burden ratio: net price / median family income
- [ ] Completion efficiency: completion rate / retention rate
- [ ] Diversity index: Herfindahl index on demographic columns
- [ ] Reduce to 50-80 meaningful features

### 1.4 Modeling
- [ ] Linear Regression baseline
- [ ] Random Forest
- [ ] XGBoost (primary model)
- [ ] Cross validation with stratified k-fold
- [ ] Track metrics: R2, RMSE, MAE

### 1.5 Explainability
- [ ] SHAP summary plot (top 15 features)
- [ ] SHAP waterfall for sample institutions
- [ ] Partial dependence plots

### 1.6 Visualizations
- [ ] Institution comparison tool
- [ ] Cost vs outcome scatter
- [ ] Geographic earnings map
- [ ] Feature importance bar chart

## Completed
- [x] Project scaffold created (2026-03-07)
