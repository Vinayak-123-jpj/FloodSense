# FloodSense Development Progress

## Current Status: ROUND 4 COMPLETE — SUBMISSION READY

### Phase Checklist
- [x] **Phase 0: Plan & Setup**
- [x] **Phase 1: Backend Core & Virtual Sensor Layer**
- [x] **Phase 2: ML Risk Engine & Data Pipeline**
- [x] **Phase 3: Alert Engine & Multilingual Bot**
- [x] **Phase 4: Frontend Development ("Hydrological Survey Atlas")**
- [x] **Phase 5: Packaging & Submission Polish**
- [x] **Fix & Audit Round 2** (OpenTopoMap/OSRM keyless tiles, 4s offline tile timeout fallback, daily resolution dataset 1990-2025, multi-horizon models, held-out 2018 validation)
- [x] **Round 3: Verification, Honesty & Submission Pack** (Night Watch dark theme map filter, pure-Python NumPy Logistic Regression baseline, per-horizon baselines on held-out 2018 set, UI metric honesty, rating curve consistency, SIMULATED badges, guided demo tour, submission answers, video script, clean git & docker checks)
- [x] **Round 4: Credibility, Real Live Data & Polish** (Copy audit removing overclaims, 7-day block bootstrap 95% CIs, station correlation & Leave-One-RIVER-Out protocol, Open-Meteo real live data mode with caching & toggle, Malayalam & Assamese multilingual alerts, PlatformIO firmware build config & Wokwi simulation, reading JSON Schema contract test, "Why not just use GloFAS?" rationale, landing hero right-half live station list, final visual QA & submission pack update)
- [x] **Round 4B: Finish and PROVE Round 4** (Retrained 11-station model on 144,639 samples with 1,000 block-bootstrap resamples, historical 31-day Kerala 2018 replay sequence demonstrating peak flood Red alerts and recession, discharge units in m³/s with p90/p97/p99.5 percentiles, native HTML/SVG confusion matrix and feature importance, startup alert burst fix with baseline Green warm-up, tight map framing and Night Watch OSM filter, 100% pytest pass, healthy docker deployment, and 22 verified desktop/mobile light/dark screenshots)

---

### Detailed Log
#### Round 4B Evidence Audit & Proof Table

| Section / Item | Status | Key File Path(s) | Test / Screenshot Proof |
|---|---|---|---|
| **0. Data-Source Toggle (Real/Simulated)** | **DONE** | `frontend/src/pages/LiveMonitorPage.tsx`, `backend/services/real_data_service.py` | `docs/screenshots/monitor-source-real.png`, `monitor-source-simulated.png`, `tests/test_api.py::test_get_real_live_station_data_success` |
| **0. Malayalam & Assamese Alerts** | **DONE** | `backend/alerts/telegram_bot.py`, `backend/alerts/alert_engine.py`, `frontend/src/components/alerts/OutboxList.tsx` | `tests/test_alerts.py::test_telegram_multilingual_formatting`, `docs/screenshots/alerts-1440-light.png`, `alerts-1440-dark.png` |
| **0. 95% Block Bootstrap CIs** | **DONE** | `scripts/train_model.py`, `reports/metrics.json`, `frontend/src/pages/ModelMethodPage.tsx` | 1,000 resamples computed in `reports/metrics.json`, rendered on `docs/screenshots/model-1440-light.png` |
| **0. Leave-One-RIVER-Out (LORO)** | **DONE** | `scripts/train_model.py`, `reports/metrics.json`, `frontend/src/pages/ModelMethodPage.tsx` | Computed across 9 river basins, displayed in LORO table on `docs/screenshots/model-1440-light.png` |
| **0. Station-Independence Note** | **DONE** | `frontend/src/pages/ModelMethodPage.tsx`, `reports/metrics.json` | Explicit callout warning of $r > 0.90$ within-basin discharge correlation rendered on `model-1440-light.png` |
| **0. Firmware CI Workflow** | **DONE** | `.github/workflows/firmware.yml`, `firmware-stub/platformio.ini` | Automated PlatformIO compile workflow for ESP32 Arduino framework |
| **0. Wokwi Simulation Project** | **DONE** | `firmware-stub/wokwi.toml`, `firmware-stub/diagram.json`, `wokwi/diagram.json` | ESP32-DevKitC-v4 + HC-SR04 ultrasonic distance sensor + 4 status LEDs wiring schematic |
| **0. "Why Not Just Use GloFAS?"** | **DONE** | `frontend/src/pages/ModelMethodPage.tsx`, `README.md`, `submission/submission_answers.md` | 4 operational pillars rendered natively on `/model` page and documented in README |
| **1. Replay Showing the Flood** | **DONE** | `data/replay_kerala_2018.json`, `frontend/src/pages/ScenarioReplayPage.tsx`, `backend/api/simulate.py` | `tests/test_simulator.py::test_replay_peak_flood_kerala`, `docs/screenshots/replay-10pct.png`, `replay-50pct.png` (Red Alert at Aluva 1773 m³/s), `replay-75pct.png`, `replay-98pct.png` (receding 607 m³/s) |
| **2. Discharge Units & Percentile Proxies** | **DONE** | `frontend/src/components/charts/WaterLevelGauge.tsx`, `frontend/src/components/charts/HydrologicalChart.tsx` | Primary axis in $m^3/s$ with $p90, p97, p99.5$ reference lines; stage height labeled `SIMULATED STAGE HEIGHT (m)` |
| **3. Real Explanations (No Dummy Features)** | **DONE** | `backend/ml/explainability.py`, `tests/test_ml.py` | Tree contributions mapped strictly to `FEATURE_COLUMNS_DAILY` (rain 1d/3d/7d, upstream discharge, soil moisture). `tests/test_ml.py::test_explainability_generator` passed |
| **4. Live Monitor Honesty & Calm Title** | **DONE** | `frontend/src/pages/LiveMonitorPage.tsx` | Titled "HYDROLOGICAL NETWORK MONITORING", source badges (`REAL`, `SIMULATED`), toggling updates state visibly |
| **5. Alerts: False Alarm Prevention** | **DONE** | `backend/alerts/alert_engine.py`, `backend/alerts/telegram_bot.py` | Baseline initialized to Green (no startup burst), Watch/Warning/Severe labels, real numbers in reasons, native disclaimer note |
| **6. Map: Dark Theme & Tight Framing** | **DONE** | `frontend/src/components/map/FloodMap.tsx`, `frontend/src/index.css` | Night Watch CSS filter on OSM tiles (`invert + hue-rotate + darken`), tight fitBounds for Kerala & Assam without ocean clipping, decluttered labels |
| **7. Model & Method Science Audit** | **DONE** | `frontend/src/pages/ModelMethodPage.tsx`, `reports/metrics.json` | 11th station included, native SVG feature bar chart, themed HTML confusion matrix, neutral highlights, Persistence 1d win acknowledged honestly |
| **8. Proof & Packaging** | **DONE** | `tests/`, `docker-compose.yml`, `docs/screenshots/` | `pytest -v`: **17/17 passed (100%)**; Docker: both containers healthy; 22 desktop (1440px) & mobile (375px) screenshots saved in `docs/screenshots/` |

---

### Verification Suites
- **Backend Unit & Contract Tests**: `pytest -v` -> **17 passed, 0 failed** in 2.58s.
- **Frontend Production Build**: `npm run build` -> **0 errors, 2373 modules transformed** in 5.64s.
- **Container Infrastructure**: Docker Compose healthy on ports `3000` (frontend Nginx) and `8000` (backend FastAPI).
- **Visual Auditing**: 22 full-page screenshots captured via Headless Chrome CLI at 1440x900 and 375x812 in both light and dark themes.

