# FloodSense Development Progress

## Current Status: ROUND 4C COMPLETE — DATA INTEGRITY & VISUAL FIXES VERIFIED

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
- [x] **Replay Verification Pass** (Data-driven per-station daily observed discharge & held-out 2018 predictions, real date labels e.g. "14 Aug 2018", start/end scrubber dates "01 Aug 2018" to "31 Aug 2018", 1.0x default what-if multiplier with "scenario, not a forecast" badge, peak discharge CSV equality & 67.7% non-identical risk days unit test, discharge gauge in m³/s with percentile proxies)
- [x] **Round 4C: Data Integrity & Visual Fixes** (Removed hardcoded defaults, single source of truth `thresholds.json`, hidden fake sensor readings in Real/Replay, zero-alert startup baseline, explainable ML risk drivers with numbers, updated GloFAS copy audit, dark/light map CSS filters & geometry cleanup, fixed replay gauge scaling & dynamic banner text, 21/21 pytest pass, 100% build pass, 20 light/dark 1440px/375px screenshots saved in `/docs/screenshots/`)

---

### Detailed Log
#### Round 4C Audit & Proof Table (Data Integrity & Visual Fixes)

| Item / Requirement | Status | Key File Path(s) | Test / Screenshot Proof |
|---|---|---|---|
| **1. Placeholder Data Removal (Critical)** | **DONE** | `frontend/src/pages/LandingPage.tsx`, `frontend/src/components/charts/WaterLevelGauge.tsx`, `data/cache/{st_id}_live.json`, `tests/test_api.py` | Removed all `35.0` & `24.5` fallbacks; pre-cached 11 real non-identical station snapshots; `test_stations_discharge_uniqueness_and_no_identical_fallbacks` PASSED |
| **2. Single Source of Truth for Thresholds** | **DONE** | `data/thresholds.json`, `frontend/public/data/thresholds.json`, `backend/services/real_data_service.py`, `backend/api/stations.py`, `tests/test_api.py` | Created `thresholds.json` with exact 1990–2017 training percentiles (p90, p97, p99.5) for all 11 stations; wired across APIs, ML, replay, alerts, and docs; `test_station_thresholds_match_thresholds_json` PASSED |
| **3. Hide Fake Sensor Data in Real/Replay Views** | **DONE** | `frontend/src/components/charts/WaterLevelGauge.tsx`, `frontend/src/components/common/Header.tsx` | Battery, RSSI, and Stage Height rendered ONLY in `SIMULATED` mode; Nav status dynamically displays active source (`REAL DATA (Open-Meteo)`, `SIMULATED SENSORS`, `REPLAY 2018`, `CACHED <date>`), removing permanent `VIRTUAL SENSORS LIVE` |
| **4. Alerts Engine & Explainable Drivers** | **DONE** | `backend/alerts/alert_engine.py`, `backend/ml/explainability.py`, `backend/api/forecast.py`, `frontend/src/pages/AlertsPage.tsx`, `tests/test_alerts.py` | Startup baseline initialized with ZERO alerts fired (`test_fresh_startup_produces_zero_alerts` PASSED); `format_driver_statement` formats real model drivers with numbers and maps seasonality to "usual monsoon-season conditions"; Outbox subtitle updated for all 4 languages |
| **5. Copy Audit ("Why Not Just Use GloFAS?")** | **DONE** | `frontend/src/pages/ModelMethodPage.tsx`, `README.md`, `submission/submission_answers.md` | Rewrote 4 pillars to factual advantages (Station Risk Classes, Local-Language Alerts, Offline Cached Resiliency, Hardware-Ready Node Blueprint) |
| **6. Maps: Theme Filters & Clean Boundaries** | **DONE** | `frontend/src/components/map/FloodMap.tsx`, `frontend/src/index.css` | Enforced exact dark theme filter `invert(1) hue-rotate(180deg) brightness(.7) contrast(.9) saturate(.4)` and light warm tint filter `sepia(0.25) saturate(0.75) contrast(0.95)` on standard OSM tiles; deleted sea-cutting dashed lines; station labels hidden by default (`zoom >= 10` or selected) |
| **7. Replay Polish & Dynamic Banner** | **DONE** | `frontend/src/pages/ScenarioReplayPage.tsx`, `frontend/src/components/charts/WaterLevelGauge.tsx` | Fixed per-station max gauge scale ($1.35 \times \text{p99.5}$); daily banner headline dynamically computed from frame risk counts and peak discharge; displayed `COLOR SOURCE: Held-Out ML Prediction (heldout_2018_model.joblib)` badge; `mode="REPLAY"` passed |
| **8. Final Verification & Screenshot Pack** | **DONE** | `tests/`, `scripts/generate_screenshots.py`, `docs/screenshots/` | `pytest -v`: **21/21 tests PASSED (100%)** in 2.59s; `npm run build`: **0 errors**; 20 desktop (1440px) and mobile (375px) screenshots in light and dark saved to `docs/screenshots/` |

#### Replay Verification Audit & Proof Table

| Item / Requirement | Status | Key File Path(s) | Test / Screenshot Proof |
|---|---|---|---|
| **1. Data-Driven Replay & Held-Out Predictions** | **DONE** | `data/replay_kerala_2018.json`, `scripts/generate_replay_dataset.py`, `backend/api/simulate.py` | `docs/screenshots/replay-42pct-data-driven.png` (shows 14 Aug 2018 with non-identical station states: Orange, Red, Yellow mix), `docs/screenshots/replay-89pct-data-driven.png` (shows 28 Aug 2018 receding mix) |
| **2. Real Date Scrubber & Start/End Labels** | **DONE** | `frontend/src/components/replay/Scrubber.tsx`, `frontend/src/pages/ScenarioReplayPage.tsx` | `docs/screenshots/replay-scrubber-real-dates.png` (Left: `01 Aug 2018`, Center: `DATE: 14 Aug 2018 (43%)`, Right: `31 Aug 2018`) |
| **3. Default 1.0x Multiplier & Scenario Disclaimer** | **DONE** | `frontend/src/components/replay/Scrubber.tsx`, `frontend/src/pages/ScenarioReplayPage.tsx` | `docs/screenshots/replay-scrubber-real-dates.png` (Defaults to 1.0x; renders `"scenario, not a forecast"` amber badge when multiplier != 1.0x) |
| **4. Peak CSV Equality & 50%+ Risk Diversity Test** | **DONE** | `tests/test_simulator.py::test_replay_kerala_2018_data_integrity_and_diversity` | `pytest -v` -> **18/18 tests PASSED (100%)** in 9.10s. Verifies exact CSV peak discharge & 21/31 days (67.7%) non-identical station risk states |
| **5. Discharge Gauge & Percentile Proxies** | **DONE** | `frontend/src/components/charts/WaterLevelGauge.tsx`, `frontend/src/components/charts/HydrologicalChart.tsx` | `docs/screenshots/discharge-gauge-percentile-proxies.png` (Primary readout displays discharge in m³/s with p90/p97/p99.5 thresholds labeled `"percentile proxies"`) |

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

