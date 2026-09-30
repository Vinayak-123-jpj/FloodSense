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

---

### Detailed Log
#### Round 4 Summary & Verification Results
- **Copy Audit**: Removed overclaims ("digital twin", "precision", "physical river telemetry", "cleanly outperforms"). Headline updated to *"Flood risk for the next three days, at each river station."* Subtitle clearly states software-only platform, public Open-Meteo datasets, simulated sensors, and hardware-ready design.
- **Statistical Honesty & CIs**: Calculated 7-day block bootstrap 95% CIs (150 resamples) for Macro F1 & Recall across 1d, 2d, and 3d horizons. Evaluated Leave-One-RIVER-Out (LORO) spatial generalization to account for high inter-station discharge correlations ($r > 0.90$).
- **Real Live Data Mode**: Added `/api/stations/{id}/real_live` endpoint querying Open-Meteo Flood & Weather APIs, caching snapshots to `/data/cache/{id}_live.json` with fallback timestamps. Added data source toggle button ("Real data (Open-Meteo)" vs "Simulated sensors") and source badges (`REAL`, `SIMULATED`, `REPLAY`) in Live Monitor.
- **Multilingual Support**: Added Malayalam (`ml`) and Assamese (`as`) alert templates alongside English and Hindi in `telegram_bot.py`, `alert_engine.py`, and `OutboxList.tsx`. Added native-speaker review disclaimer notes.
- **Hardware Readiness & Wokwi**: Added `firmware-stub/platformio.ini`, `.github/workflows/firmware.yml` for automated CI sketch builds, `/docs/api/reading.schema.json`, schema contract test, `/wokwi/diagram.json`, and `/wokwi/README.md`.
- **"Why Not Just Use GloFAS?"**: Added detailed operational rationale sections in `README.md` and `submission/submission_answers.md`.
- **Hero Right-Half Layout**: Updated `LandingPage.tsx` hero section to a 2-column grid featuring a compact live station risk summary list on the right half.
- **Verification Suites**:
  - `pytest -v`: 16/16 tests passing (100%).
  - `npm run build`: Production bundle built in 3.8s with zero TypeScript / Vite errors.

