# FloodSense Development Progress

## Current Status: ROUND 6B VERIFICATION AUDIT COMPLETE — RETRAIN PROVED & AUDITED

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
- [x] **Round 4B: Finish and PROVE Round 4** (Retrained 11-station model on 144,639 samples with 1,000 block-bootstrap resamples, historical 31-day Kerala 2018 replay sequence, discharge units in m³/s with percentiles, native HTML/SVG confusion matrix and feature importance, 100% pytest pass, healthy docker deployment, and 22 verified screenshots)
- [x] **Replay Verification Pass** (Data-driven per-station daily observed discharge & held-out 2018 predictions, real date labels e.g. "14 Aug 2018", start/end scrubber dates "01 Aug 2018" to "31 Aug 2018", 1.0x default what-if multiplier with scenario disclaimer, peak discharge CSV equality & 67.7% non-identical risk days unit test)
- [x] **Round 4C: Data Integrity & Visual Fixes** (Removed hardcoded defaults, single source of truth `thresholds.json`, hidden fake sensor readings in Real/Replay, zero-alert startup baseline, explainable ML risk drivers with numbers, updated GloFAS copy audit, dark/light map CSS filters & geometry cleanup, 21/21 pytest pass, 100% build pass)
- [x] **ROUND 5: Integrity Audit & Feature Freeze** (11-Station snapped grid cell coordinates & mainstem thresholds, 100% class agreement, strict monotonicity test, NOW vs FORECAST D+1..D+3 chips & dates, real calendar dates on chart x-axis without minute timestamps, Data Freshness Panel, top 3 SHAP/pred_contrib drivers without generic filler text, IST timestamps, DEMO ALERT generator with [DEMO] tag, Night Watch #0C141B map tile filter, PlatformIO firmware CI & reading.schema.json validation test, 25/25 pytest pass, 0-error build pass, 20 light/dark screenshots)
- [x] **ROUND 6: Data Truth Audit & Verification** (Zero hardcoded values, live Open-Meteo API grid cell equality test, 1990-2017 historical stats computed in code with CSV SHA256 hashes, 100% triple comparison match between Live API, Backend `/api/stations`, and UI, out-of-bounds 1.5x max guard returning "Data check failed", map popup discharge in m³/s with p90/p97/p99.5 thresholds and dark theme contrast fix, 10-day Live Monitor chart scaling `[0, 1.2 x max]`, driver 1 threshold statement format, CARTO Voyager English map tiles, 26/26 pytest pass, 0-error build pass, 11-station Live Monitor dark screenshots)
- [x] **ROUND 6B VERIFICATION: Retrain Audit & Spatial Generalization** (Retrained LightGBM & Logistic Regression daily models on 137,967 rows across 11 stations, exported dynamic metrics.json, 100% triple match on 2018 high-risk day counts between direct CSVs, metrics.json, and UI, Leave-One-River-Out benchmark results per river basin, verified mathematical invariance of held-out Kerala 2018 metrics due to isolated Assam mainstem updates, removed Numaligarh from Brahmaputra mainstem downstream table, labeled all stations as "nearest main-channel grid cell", 27/27 pytest pass, 0-error build pass)

---

## Round 6 Data Truth Audit & Provenance Log

### Section 1: Provenance of Every Number (11-Station Hydrological Data Audit Table)

| Station ID | Station Name | Requested Lat/Lon | Returned Grid Cell Lat/Lon | CSV SHA256 | Training Rows (N) | Min (m³/s) | Med (m³/s) | p90 (Yellow) | p97 (Orange) | p99.5 (Red) | Max (m³/s) | 2018 Peak (m³/s) | Live Q (m³/s) | Percentile Rank | Computed Class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `KL-PER-01` | Neeleswaram | 10.1416, 76.5781 | 10.1250, 76.5750 | `6b4048d4` | 10,227 | 0.0 | 93.0 | 400.8 | 549.8 | 754.9 | 1173.9 | 1639.6 | 1.0 | 25.0% | Green |
| `KL-PER-02` | Aluva | 10.1076, 76.3516 | 10.1250, 76.3750 | `2eec920e` | 10,227 | 0.0 | 97.6 | 437.5 | 600.2 | 809.7 | 1249.3 | 1773.2 | 122.6 | 53.6% | Green |
| `KL-PAM-01` | Chengannur | 9.3175, 76.6122 | 9.3250, 76.6250 | `ba3427e7` | 10,227 | 0.0 | 53.6 | 167.7 | 233.4 | 325.5 | 552.4 | 581.1 | 50.9 | 49.0% | Green |
| `KL-MUV-01` | Muvattupuzha | 9.9813, 76.5772 | 9.9750, 76.5750 | `c6c9cca3` | 10,227 | 0.0 | 8.3 | 41.8 | 59.7 | 84.5 | 245.0 | 146.2 | 10.1 | 53.3% | Green |
| `KL-CHA-01` | Chalakudy | 10.3070, 76.3323 | 10.3250, 76.3250 | `c0dd5f2d` | 10,227 | 0.0 | 23.3 | 156.4 | 221.4 | 290.6 | 461.4 | 630.0 | 36.0 | 56.1% | Green |
| `KL-ACH-01` | Thumpamon | 9.2560, 76.7110 | 9.2750, 76.7250 | `97b55d57` | 7,305 | 0.0 | 5.9 | 37.8 | 56.8 | 83.2 | 154.2 | 154.2 | 11.7 | 62.7% | Green |
| `AS-BRA-01` | Guwahati | 26.1833, 91.7500 | 26.1750, 91.7750 | `c2fff391` | 10,227 | 0.0 | 0.7 | 20.0 | 31.4 | 52.1 | 97.2 | 54.2 | 4.9 | 71.6% | Green |
| `AS-BRA-02` | Dibrugarh | 27.4728, 94.9120 | 27.4750, 94.9250 | `2e4e9ba1` | 10,227 | 0.0 | 0.2 | 3.4 | 5.0 | 8.2 | 18.6 | 5.1 | 0.7 | 58.0% | Green |
| `AS-KOP-01` | Kampur | 26.1500, 92.5833 | 26.1750, 92.5750 | `b16347fc` | 10,227 | 0.0 | 45.1 | 693.1 | 1155.1 | 1938.7 | 5235.0 | 394.4 | 189.1 | 65.5% | Green |
| `AS-DHA-01` | Numaligarh | 26.5667, 93.7333 | 26.5750, 93.7250 | `6be4572f` | 10,227 | 0.0 | 61.2 | 800.7 | 1118.4 | 1671.5 | 3053.9 | 1118.4 | 288.7 | 66.5% | Green |
| `AS-JIA-01` | Tezpur | 26.6333, 92.8000 | 26.6250, 92.8250 | `a78755f6` | 10,227 | 0.0 | 4774.3 | 27063.5 | 36811.9 | 45261.7 | 58343.5 | 32209.7 | 11297.0 | 65.5% | Green |

---

### Triple Comparison: Live Open-Meteo API vs Backend `/api/stations` vs UI (`thresholds.json`)

| Station ID | Station Name | Live Open-Meteo API Q (m³/s) | Backend `/api/stations` Q (m³/s) | UI Source (`thresholds.json`) Q (m³/s) | Triple Match Status |
|---|---|---|---|---|---|
| `KL-PER-01` | Neeleswaram | 1.0 | 1.0 | 1.0 | **MATCH (100%)** |
| `KL-PER-02` | Aluva | 122.6 | 122.6 | 122.6 | **MATCH (100%)** |
| `KL-PAM-01` | Chengannur | 50.9 | 50.9 | 50.9 | **MATCH (100%)** |
| `KL-MUV-01` | Muvattupuzha | 10.1 | 10.1 | 10.1 | **MATCH (100%)** |
| `KL-CHA-01` | Chalakudy | 36.0 | 36.0 | 36.0 | **MATCH (100%)** |
| `KL-ACH-01` | Thumpamon | 11.7 | 11.7 | 11.7 | **MATCH (100%)** |
| `AS-BRA-01` | Guwahati | 4.9 | 4.9 | 4.9 | **MATCH (100%)** |
| `AS-BRA-02` | Dibrugarh | 0.7 | 0.7 | 0.7 | **MATCH (100%)** |
| `AS-KOP-01` | Kampur | 189.1 | 189.1 | 189.1 | **MATCH (100%)** |
| `AS-DHA-01` | Numaligarh | 288.7 | 288.7 | 288.7 | **MATCH (100%)** |
| `AS-JIA-01` | Tezpur | 11297.0 | 11297.0 | 11297.0 | **MATCH (100%)** |

---

### Verification Summary
- **Backend Test Suite**: `pytest -v` -> **26/26 tests PASSED (100%)** in 11.95s.
- **Frontend Production Build**: `npm run build` -> **0 errors (2,373 modules transformed)** in 3.99s.
- **Grid Cell Equality Contract**: `test_live_and_history_grid_cell_equality` passed.
- **Out of Bounds Safety Guard**: `test_live_value_outside_1_5x_max_returns_data_check_failed` passed.
- **Live Monitor Screenshot Audit**: 11 station dark theme full-page screenshots captured in `docs/screenshots/live-monitor-{st_id}-dark.png`.
