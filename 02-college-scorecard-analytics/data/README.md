# Data Download — College Scorecard

## Quick Download

1. Go to **https://collegescorecard.ed.gov/data**
2. Download **"Most Recent Institution-Level Data"**
3. Extract the CSV and place it in this `data/raw/` directory

The file will be named something like `Most-Recent-Cohorts-Institution_04292025.csv`.

## What It Contains

~7,000+ institutions with 3,000+ variables covering:
- Admissions (acceptance rates, SAT/ACT scores)
- Cost (tuition, net price, fees)
- Student demographics
- Completion and retention rates
- Post-graduation outcomes (earnings, debt, repayment)

## Special Values

| Value | Meaning |
|-------|---------|
| `PrivacySuppressed` | Data suppressed for privacy (small cohorts) |
| `NULL` | Missing |

The pipeline handles both automatically.
