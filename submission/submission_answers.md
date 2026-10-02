# FloodSense — FOSSEE Open Hardware National Make-A-Thon 2026 Submission Answers

## 1. Project Title & Short Summary
**Project Title**: FloodSense — Software-Only Flood Early-Warning Platform & Hydrological Survey Atlas  
**Sub-Theme**: Disaster Detection & Early Warnings (Floods Monitoring)  
**Short Description**: FloodSense is an end-to-end software-only flood early-warning platform built for the FOSSEE Make-A-Thon 2026. It emulates physical ESP32 IoT river gauging nodes sending JSON telemetry over HTTP/WebSocket, processes 36-year daily Open-Meteo GloFAS river discharge reanalysis data (1990–2025 across 10 river basins in Kerala and Assam), and applies a leakage-audited LightGBM multi-horizon classifier to deliver 24h to 72h early warning alert notifications in English, Hindi, Malayalam, and Assamese.

---

## 2. Problem Statement
Monsoon flood disasters in river basins across India (such as the August 2018 Kerala floods and annual Brahmaputra inundations in Assam) cause catastrophic loss of life and property. Existing early warning mechanisms often suffer from:
1. **Delayed Lead Times**: Notifications dispatched only after river gauges cross physical danger marks.
2. **Alarm Fatigue**: Repeated flapping alerts caused by sensor noise near danger thresholds.
3. **Data Disconnect**: Lack of integrated visual tools to evaluate "what-if" rainfall scenarios.

---

## 3. Solution Overview
FloodSense solves these challenges through a unified 5-layer software architecture:
- **Virtual Sensor Layer**: `SensorNodeSimulator` emulates solar-powered ESP32 ultrasonic water level nodes with Gaussian measurement noise, battery drain/solar recharge dynamics, and packet dropouts.
- **Data & Feature Engineering Pipeline**: Long-term daily hydrological dataset (115,502 daily rows from 1990 to 2025 across 11 stations) featuring daily rolling rainfall (1d, 3d, 7d, 14d, 30d), 3d discharge rate-of-change, and 7-day Antecedent Precipitation Index (API).
- **Leakage-Audited Multi-Horizon ML Classifier**: LightGBM model trained on shifted future targets ($t+1\text{d}, t+2\text{d}, t+3\text{d}$) evaluated across 3 rigorous validation protocols (7-day block bootstrap 95% CIs, held-out 2018 event set, and Leave-One-RIVER-Out LORO spatial generalization).
- **Hysteresis & Multilingual Alert Engine**: State machine with 10% threshold deadbands and 2-hour minimum suppression windows to eliminate alert flapping, delivering outbox notifications in English, Hindi, Malayalam, and Assamese.
- **Hydrological Survey Atlas Frontend**: Desaturated OpenStreetMap Leaflet atlas with keyless tiles, 4-second vector GeoJSON boundary fallback, 2018 disaster scrubber, what-if stress test slider, and skippable guided demo tour.

---

## 4. Technology Stack
- **Backend Core**: Python 3.11 / FastAPI, SQLAlchemy, SQLite, Uvicorn, WebSockets.
- **Machine Learning Engine**: LightGBM, Pure-Python NumPy Logistic Regression, Pandas, NumPy, Joblib.
- **Frontend UI**: React 18, TypeScript, Vite, Tailwind CSS, Leaflet, React-Leaflet, Lucide Icons.
- **DevOps & Packaging**: Docker, Docker Compose, PlatformIO CI.

---

## 5. Key Novelty & Engineering Highlights
1. **Strict Data Leakage Audit**: Predicts future risk at $t+1\text{d}, t+2\text{d}, t+3\text{d}$ using ONLY historical data available up to time $t$. Enforces a 7-day chronological split gap, Leave-One-RIVER-Out (LORO) cross-validation, and a genuinely out-of-sample held-out 2018 event validation set.
2. **State Transition Hysteresis**: Prevents repeated alert spamming when river levels oscillate near danger thresholds.
3. **Keyless Offline Resilience**: Map layer automatically falls back to bundled coastal boundary vector GeoJSON (`KERALA_BOUNDARY_GEOJSON` and `ASSAM_BOUNDARY_GEOJSON`) if network connection fails or tile load times exceed 4 seconds.
4. **Physical Override Safety Net**: High-risk physical overrides ensure that any station crossing physical channel danger marks is escalated to Red regardless of ML model output.
5. **Real Live Open-Meteo Stream & Hardware Simulator**: Dual mode allowing live public reanalysis/forecast streaming or hardware-ready virtual sensor telemetry ingestion.

---

## 6. Scientific Limitations & Data Honesty
- **Modeled GloFAS Discharge**: River discharge values ($m^3/s$) are obtained from Open-Meteo GloFAS reanalysis modeling, NOT physical gauge height meters.
- **Percentile Proxies**: Risk labels are defined using station-specific historical training period discharge percentiles (p90=Yellow, p97=Orange, p99.5=Red), NOT official CWC stage thresholds.
- **Daily Resolution Limit**: GloFAS discharge data updates daily. Intra-day flash floods under 3 hours rely on antecedent rainfall indices.
- **Past Observed Rainfall**: Features use observed past rainfall, NOT future numerical weather forecast predictions.
- **Max Horizon Cap**: Prediction lead times are strictly capped at the 3-day maximum horizon.

---

## 7. Open Hardware Deployment Roadmap (Planned, Not Built This Round)
*Note: There is no physical hardware deployed in Round 1/2. The hardware design below is planned for future physical field deployment.*
- **Microcontroller**: ESP32-WROOM-32U with external dipole antenna.
- **Telemetry Module**: SIM7000G LTE-M/NB-IoT / GSM cellular module.
- **Sensor Transducer**: JSN-SR04T waterproof ultrasonic distance sensor ($20\text{ cm} - 600\text{ cm}$ range) + tipping bucket rain gauge.
- **Power Subsystem**: 10W solar panel + 18650 LiFePO4 battery pack + TP4056 solar charge controller with sleep cycle management.
- **Target BOM Cost**: ₹3,990 INR (~$48 USD) per solar-autonomous node.

---

## 8. Why Not Just Use GloFAS Directly?
Global systems like GloFAS provide essential global hydrological forecasts, but they are not designed as complete, end-to-end local early-warning platforms for municipal emergency responders. FloodSense builds on GloFAS and Open-Meteo data to deliver actionable local capability:
1. **Station Risk Classes & Thresholding**: GloFAS outputs coarse volumetric discharge ($m^3/s$). FloodSense computes station-specific historical baseline percentiles (p90, p97, p99.5) and classifies risk into Green, Yellow, Orange, and Red states with SHAP feature explanations.
2. **Local-Language Actionable Alerts**: GloFAS provides global gridded data arrays. FloodSense translates high-risk conditions into actionable alerts in English, Malayalam, Assamese, and Hindi paired with nearest evacuation shelter links.
3. **Alert Flapping & Hysteresis Control**: Raw threshold alerts fluctuate rapidly near danger marks. FloodSense enforces a state-machine hysteresis engine to prevent alert fatigue among emergency responders.
4. **Offline Resilience & Hardware-Ready Blueprint**: FloodSense bundles offline historical datasets and cached snapshots for operation during network outages, and provides an open ESP32 hardware node blueprint (planned for physical deployment, simulated this round).

