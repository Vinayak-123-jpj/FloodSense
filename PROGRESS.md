# FloodSense Development Progress

## Current Status: Phase 2 Completed -> Phase 3 In Progress

### Phase Checklist
- [x] **Phase 0: Plan & Setup** (PLAN.md approved, git repo initialized, directory structure designed)
- [x] **Phase 1: Backend & Virtual Sensor Layer** (FastAPI REST API, WebSocket `/ws/live`, SQLite database, virtual sensor simulator daemon, firmware blueprint)
- [x] **Phase 2: ML Risk Engine & Explainability** (Open-Meteo real data fetcher, feature engineering, LightGBM classifier, 29h Kerala 2018 backtest lead time, model report & saved charts)
- [ ] **Phase 3: Alert Engine & Multilingual Bot**
- [ ] **Phase 4: Frontend Development ("Hydrological Survey Atlas")**
- [ ] **Phase 5: Packaging, Tests & Submission Polish**

---

### Detailed Log
#### Phase 2 Summary: ML Risk Engine & Explainability
- Built real data fetcher `scripts/fetch_data.py`:
  - Queried Open-Meteo Historical Weather API (hourly precipitation) & Flood API (daily river discharge).
  - Saved 35,064 real hourly records into `/data/raw/kerala_weather_flood.csv` and `/data/raw/assam_weather_flood.csv`.
- Implemented `backend/ml/feature_engineering.py`:
  - Computed 6h, 24h, 72h rolling precipitation, river discharge rates of change, antecedent wetness index (API), and seasonality.
- Implemented training script `scripts/train_model.py`:
  - Enforced strict chronological time-based train/test split (80% train / 20% test) to eliminate data leakage.
  - Trained LightGBM classifier achieving **99.89% overall accuracy** and **97.31% Macro F1**.
  - Compared against single-variable threshold baseline (0.69 Macro F1).
  - Evaluated Kerala August 2018 historic flood backtest: **29 hours of early warning lead time** prior to peak river discharge.
  - Rendered and saved charts to `/reports/`: `confusion_matrix.png`, `feature_importance.png`, `kerala_2018_backtest.png`.
  - Generated comprehensive `/reports/model_report.md` detailing metrics, baseline comparison, lead times, and honest failure modes.
- Implemented `backend/ml/explainability.py`:
  - Outputted top 3 plain-language risk driver bullet points per prediction.
- Implemented `backend/ml/predictor.py`:
  - Executed LightGBM model inference with physical safety threshold overrides and rule-based fallback engine.
- Passed 9 automated unit tests (`pytest`).
