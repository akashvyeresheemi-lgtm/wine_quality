# 🍷 Alcohol Quality Prediction

An end-to-end machine learning project: predict the quality score (0–10) of red wine from 11 chemical
properties, with an interactive Streamlit dashboard, explainability, history tracking and PDF reports.

## Features
- **Dashboard** with live prediction, quality ring, confidence, and dataset KPIs
- **Explainability**: per-feature impact on each prediction and a radar comparison against top-rated wines
- **Health & safety insights** and winemaking recommendations (rule-based)
- **Batch prediction**: upload a CSV (comma or semicolon separated) with the 11 properties; get a quality score, rating, confidence and safety check per wine, a CSV download, and an accuracy check if the file has a quality column
- **Explainability**: plain-language reasons for each score, impact chart, and what-if scenarios showing which change would help most
- **Standards comparison**: animated chart of the wine against OIV reference limits, with a safe / caution / not recommended verdict (limits are editable in `src/standards.py`)
- **History** stored in SQLite, with filtering, CSV export and a trend chart
- **PDF reports** generated with ReportLab
- **Analytics**: dataset EDA, correlation matrix, model comparison, predicted-vs-actual, feature importance

## Quick start
```bash
pip install -r requirements.txt
python train_model.py        # optional: the app trains automatically on first run
streamlit run app.py
```

## Project structure
```
app.py              Streamlit dashboard (6 pages)
train_model.py      Model benchmarking, tuning and export
src/ml.py           Features, prediction, confidence, explanations, insights
src/db.py           SQLite prediction history
src/report.py       PDF report builder
src/standards.py    OIV reference limits and safety verdict
src/batch.py        CSV batch prediction
src/style.py        Dark theme CSS and HTML components
data/               winequality-red.csv (UCI, 1,599 samples)
models/             wine_model.joblib, metrics.json
```

## Model results (held-out 20% test set)
| Model | Test RMSE | R² |
|---|---|---|
| Ridge Regression | 0.632 | 0.382 |
| Gradient Boosting | 0.599 | 0.443 |
| Random Forest (tuned, deployed) | 0.549 | 0.533 |
| Extra Trees | 0.534 | 0.557 |

About 70% of predictions land within ±0.5 of the expert score. Random Forest is deployed because its
individual trees give the per-prediction confidence value. Extra Trees scored slightly better and could be
swapped in with the same approach.

## How the numbers are computed
- **Confidence:** share of trees whose prediction is within ±0.5 of the ensemble average.
- **Feature impact:** score minus the score when that one property is set to the dataset mean.

## About the safety verdict
Limits come from the OIV International Code of Oenological Practices (total SO2 150 mg/L for red wine, citric
acid 1 g/L, volatile acidity 20 meq/L, minimum 8.5% vol alcohol). Chlorides, sulphates and fixed acidity are
marked with a dagger because they were not re-verified against the source text, and residual sugar, pH and
free SO2 are advisory ranges only. National regulators (FSSAI, EU, TTB) can differ, so adjust `LIMITS` for your
jurisdiction. The verdict is a screening, not a laboratory test or safety certificate.

## Ideas to extend
Add the white-wine dataset with a wine-type input, SHAP explanations, user login, Docker deployment,
or Streamlit Community Cloud hosting.

## Limitations
Red wine only; quality labels are subjective; rare extreme scores are hard to predict. Health notes are
general information, not medical advice.
