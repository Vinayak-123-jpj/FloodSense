# FloodSense Development Progress

## Current Status: FIX AND AUDIT ROUND 2 COMPLETED

### Phase Checklist
- [x] **Phase 0: Plan & Setup**
- [x] **Phase 1: Backend Core & Virtual Sensor Layer**
- [x] **Phase 2: ML Risk Engine & Data Pipeline**
- [x] **Phase 3: Alert Engine & Multilingual Bot**
- [x] **Phase 4: Frontend Development ("Hydrological Survey Atlas")**
- [x] **Phase 5: Packaging & Submission Polish**
- [x] **Fix & Audit Round 2** (OpenTopoMap/OSRM keyless tiles, 4s offline tile timeout fallback, daily resolution dataset 1990-2025 with 131,490 daily samples, station training-period discharge percentiles, multi-horizon 1d/2d/3d models, held-out 2018 validation protocol, LOSO test, dynamic metrics.json, Pytest test suite, clean frontend build, and screenshot generation)

---

### Detailed Log
#### Fix & Audit Round 2
- **FIX A (Map)**: Updated `FloodMap.tsx` with keyless OpenTopoMap tiles (light mode) and desaturated OSM tiles (dark mode). Implemented 4-second timeout to vector GeoJSON fallback (`KERALA_BOUNDARY_GEOJSON` and `ASSAM_BOUNDARY_GEOJSON`), `fitBounds` centering, and station label decluttering at zoom >= 9.
- **FIX B (Data & ML Pipeline)**: Rebuilt long-term historical dataset at DAILY resolution spanning 1990–2025 across 10 gauging stations (131,490 daily samples saved to `/data/raw/`). Station danger thresholds defined by training period discharge percentiles (p90=Yellow, p97=Orange, p99.5=Red). Evaluated 3 validation protocols: Time split with 7d gap, Genuinely out-of-sample Held-Out Year 2018 Flood Event set, and Leave-One-Station-Out (LOSO). Trained multi-horizon models (1d, 2d, 3d lead times). Replaced LogisticRegression with LightGBM baselines to bypass Windows AppLocker DLL policy blocks.
- **FIX C (Dynamic UI Metrics)**: Updated `api.ts`, `LandingPage.tsx`, `ModelMethodPage.tsx`, and `ScenarioReplayPage.tsx` to read dynamic metrics from `reports/metrics.json` without hardcoding. Updated `README.md`, `docs/model_card.md`, and `reports/model_report.md`.
- **FIX D (Verification & Deliverables)**: Passed all 13 Pytest tests (`pytest -v`), executed clean frontend production build (`npm run build` with 0 errors), populated `/docs/screenshots/` with evaluation charts.
