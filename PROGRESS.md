# FloodSense Development Progress

## Current Status: ROUND 3 (VERIFICATION, HONESTY & SUBMISSION PACK) COMPLETED

### Phase Checklist
- [x] **Phase 0: Plan & Setup**
- [x] **Phase 1: Backend Core & Virtual Sensor Layer**
- [x] **Phase 2: ML Risk Engine & Data Pipeline**
- [x] **Phase 3: Alert Engine & Multilingual Bot**
- [x] **Phase 4: Frontend Development ("Hydrological Survey Atlas")**
- [x] **Phase 5: Packaging & Submission Polish**
- [x] **Fix & Audit Round 2** (OpenTopoMap/OSRM keyless tiles, 4s offline tile timeout fallback, daily resolution dataset 1990-2025, multi-horizon models, held-out 2018 validation)
- [x] **Round 3: Verification, Honesty & Submission Pack** (Night Watch dark theme map filter, pure-Python NumPy Logistic Regression baseline, per-horizon baselines on held-out 2018 set, UI metric honesty, rating curve consistency, SIMULATED badges, guided demo tour, submission answers, video script, clean git & docker checks)

---

### Detailed Log
#### Round 3 Summary
- **Map Polish (A)**: Enforced `.dark .leaflet-tile-pane` dark theme filter (`invert(1) hue-rotate(180deg) desaturate(0.8) brightness(0.55)`). Replaced crude ocean-crossing outlines in `regionOutlines.ts` with real coastal-tracing polygon coordinates for Kerala and Assam boundaries and channel paths for Periyar, Pamba, and Brahmaputra rivers.
- **ML Honesty & Pure-Python Baseline (B)**: Implemented `LogisticRegressionNumPy` (OvR Logistic Regression in pure Python/NumPy without compiled C-extensions). Evaluated LightGBM, Linear Logistic Regression, Persistence, and Threshold Rule baselines across 1d, 2d, 3d horizons on the held-out 2018 test set. Shifted landing headline metrics to Macro F1 (84.71%) vs Persistence (85.58%), High-Risk Recall (91.40%), and Warning Lead Time (2 Days / 48 Hours, capped at 3-day max horizon). Exported per-station 2018 lead times, actual Orange/Red days, and false alarms.
- **Simulator Rating Curve & SIMULATED Badges (C)**: Standardized stage-to-discharge rating curve conversion ($Q = a \cdot (h - h_0)^b$). Added `SimulatedBadge` (`[SIMULATED TELEMETRY]`) to Live Monitor and WaterLevelGauge header cards.
- **Guided Demo Tour (E)**: Created `GuidedDemoModal.tsx` on the Landing Page providing a skippable 5-step interactive tour of Live Monitor, Kerala 2018 Replay, What-If Slider, Alert Outbox, and Model Audit page.
- **Submission Pack (F)**: Created `submission/submission_answers.md`, `scripts/record_demo.md`, `scripts/generate_screenshots_docs.py`, and updated `README.md`, `docs/model_card.md`, and `reports/model_report.md`.
- **Final Checks (G)**: 13/13 Pytest tests passed (`pytest -v`), frontend compiled with 0 errors (`npm run build`).
