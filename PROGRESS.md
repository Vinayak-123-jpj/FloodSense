# FloodSense Development Progress

## Current Status: ALL PHASES & AUDIT COMPLETED (Push-Ready)

### Phase Checklist
- [x] **Phase 0: Plan & Setup** (PLAN.md approved, git repo initialized, directory structure designed)
- [x] **Phase 1: Backend & Virtual Sensor Layer** (FastAPI REST API, WebSocket `/ws/live`, SQLite database, virtual sensor simulator daemon, firmware blueprint)
- [x] **Phase 2: ML Risk Engine & Explainability** (Open-Meteo real data fetcher, feature engineering, LightGBM classifier, 53h Kerala 2018 backtest lead time, model report & saved charts)
- [x] **Phase 3: Alert Engine & Multilingual Bot** (Hysteresis state tracking, deduplication, multilingual Telegram bot in English & Hindi, OSRM evacuation route links, in-app Alert Outbox)
- [x] **Phase 4: Frontend Development ("Hydrological Survey Atlas")** (React + Vite + TypeScript + Tailwind CSS, desaturated Leaflet maps with contour polygons, 6 complete views, Day Survey & Night Watch themes)
- [x] **Phase 5: Packaging, Tests & Submission Polish** (Multi-stage Docker containers, Docker Compose, 12 passing Pytest tests, in-depth documentation in `/docs/`, 3-minute video script in `scripts/record_demo.md`, README.md)
- [x] **Fix & Audit Pass** (Keyless Carto tiles with OSM fallback & GeoJSON vector overlay, baseline simulator Green state, ML target redefinition to t+24h future lead time with 72h split gap, dynamic `metrics.json` integration, restyled editorial field-report figures)

---

### Detailed Log
#### Fix & Audit Pass Summary
1. **Map Tiles & Offline Resilience**:
   - Switched map tile URLs to keyless Carto endpoints (`https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png` & `dark_nolabels`, subdomains `"abcd"`).
   - Configured OpenStreetMap tile fallback with theme CSS filters (`saturate(0.3)`).
   - Bundled simplified GeoJSON region boundaries (`KERALA_BOUNDARY_GEOJSON` & `ASSAM_BOUNDARY_GEOJSON`) to guarantee zero blank maps even when completely offline.
   - Added `fitBounds` region switcher controls directly on the map.
   - Added labels and dual-coded shape icons (`● ▲ ◆ ⬢`) to every station marker alongside hover tooltips.
2. **Baseline Live Simulator Fix**:
   - Fixed `sensor_simulator.py` water level relaxation decay so live mode starts and stays in a clean **mostly GREEN baseline state with occasional Yellow**.
   - Orange / Red alerts appear strictly during Replay mode or when the What-If rain slider is raised above 1.5x.
3. **ML Data Leakage Audit**:
   - Identified that predicting risk at time $t$ using discharge at time $t$ caused target leakage.
   - Redefined the ML target variable to **future risk level at $t + 24\text{h}$ ($Y_{t+24\text{h}}$)** using features computed exclusively from data available up to time $t$.
   - Enforced a **72-hour chronological gap** between training set end and test set start to eliminate rolling window overlap across the split boundary.
   - Evaluated ML model against Persistence ($Y_{\text{pred}} = \text{current\_risk\_at\_t}$) and Threshold Rule baselines.
   - Exported dynamic machine-readable `reports/metrics.json` and `frontend/public/reports/metrics.json`.
4. **Dynamic UI Metrics Integration**:
   - Updated `LandingPage.tsx` and `ModelMethodPage.tsx` to dynamically load `/reports/metrics.json` rather than hardcoding numbers.
   - Restyled the landing page stat cards as **editorial field-report figures with thin 1px rules**.
5. **Verification**:
   - Passed 12 automated unit tests (`pytest`).
   - Clean production bundle (`npm run build`).
