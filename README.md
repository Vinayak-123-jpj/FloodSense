# FloodSense — Software-Only Flood Early-Warning Platform & Hydrological Survey Atlas
### FOSSEE Open Hardware National Make-A-Thon 2026 (Disaster Detection & Early Warnings: Floods Monitoring)

[![Licence: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11](https://img.shields.io/badge/Python-3.11-teal.svg)](backend/)
[![React: 18](https://img.shields.io/badge/React-18-61dafb.svg)](frontend/)
[![Held-Out 2018 Macro F1: 84.71%](https://img.shields.io/badge/HeldOut_2018_Macro_F1-84.71%25-success.svg)](reports/metrics.json)
[![ESP32 Firmware CI](https://github.com/YOUR_USERNAME/floodsense/actions/workflows/firmware.yml/badge.svg)](.github/workflows/firmware.yml)

**FloodSense** is a software-only flood early-warning platform and hydrological survey atlas that emulates physical IoT sensor grids to deliver 24-to-72-hour early warning predictions across river catchments in Kerala and Assam. Powered by a FastAPI backend, a leakage-audited LightGBM machine learning classifier trained on 131,490 daily GloFAS records (1990–2025), and a desaturated "Hydrological Survey Atlas" React frontend, FloodSense features hysteresis alert deduplication, multilingual Telegram warnings (English, Hindi, Malayalam & Assamese), OpenStreetMap evacuation routing, and an open-hardware ESP32 blueprint.

---

## 1. Problem Statement & Architecture

During monsoon seasons in India, delayed flood notifications severely hamper disaster response. For the **FOSSEE Open Hardware National Make-A-Thon 2026**, sensors are simulated by a virtual sensor layer (`sensor_simulator.py`) sending JSON telemetry payloads identical to real ESP32 nodes over HTTP/WebSocket.

```mermaid
graph TD
    subgraph Virtual Sensor Layer & External Data
        VS[Sensor Emulator / ESP32 Firmware Stub] -->|HTTP POST /api/readings| API[FastAPI Backend Core]
        OM[Open-Meteo Weather & Flood APIs / Offline CSVs] -->|Data Fetcher| DB[(SQLite Database)]
    end

    subgraph Core ML Engine & Alerts
        API -->|Readings & Telemetry| DB
        ML[LightGBM Multi-Horizon Classifier] -->|24h-72h Predictions| DB
        HYST[Hysteresis Alert Engine] -->|Multilingual Messages| BOT[Telegram Bot / In-App Outbox]
    end

    subgraph Hydrological Survey Atlas Frontend
        API -->|REST & WebSocket /ws/live| FE[React + Vite + TypeScript Frontend]
        FE -->|Desaturated Atlas Map| MAP[Interactive Leaflet Atlas]
        FE -->|72h Forecast Band| CHARTS[Hydrological Forecast Charts]
        FE -->|Timeline Scrubber| REPLAY[Kerala 2018 & Assam Historical Replay]
    end
```

---

## 2. Quickstart (Run in 3 Commands)

Execute the full stack using Docker Compose:

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/floodsense.git
cd floodsense

# 2. Launch complete platform with single command
docker compose up --build
```

- **Frontend Application**: `http://localhost:3000`
- **FastAPI OpenAPI Documentation**: `http://localhost:8000/docs`
- **Backend Health Diagnostics**: `http://localhost:8000/api/health`

---

## 3. Platform Screenshots

![Landing Page Atlas](docs/screenshots/landing_page_atlas.png)

![Live Monitor Control Room](docs/screenshots/live_monitor_room.png)

![Kerala 2018 Historical Replay](docs/screenshots/kerala_2018_replay_scrubber.png)

![Multilingual Alert Outbox](docs/screenshots/alert_outbox_multilingual.png)

![Model Science Audit Report](docs/screenshots/model_science_audit.png)

---

## 4. Machine Learning Audit & Side-by-Side Baselines

### Held-Out 2018 Flood Event Validation Set (100% Out-of-Sample, 11 Stations)

| Prediction Horizon | Model / Benchmark | Macro F1 (95% CI) | Orange/Red Recall | Orange/Red Precision | False Alarm Rate (FAR) | False Alarms / Stn-Yr | Accuracy |
|---|---|---|---|---|---|---|---|
| **t + 1d (24h)** | **LightGBM (Primary)** | 83.57% [81.08%, 85.54%] | **90.93% [87.71%, 93.74%]** | 75.29% | 4.15% | 13.45 | 90.36% |
| | Linear (Logistic Regression) [Pure NumPy] | 60.95% [59.14%, 62.64%] | 70.36% | 74.73% | 3.26% | 10.73 | 88.47% |
| | **Persistence Baseline** | **85.01% [82.71%, 86.84%]** | 86.90% [83.54%, 89.71%] | **80.56%** | **2.92%** | **9.45** | **91.71%** |
| | Rainfall Threshold Rule | 48.86% [45.56%, 52.29%] | 97.38% | 32.48% | 27.28% | 91.27 | 61.94% |
| **t + 2d (48h)** | **LightGBM (Primary)** | **74.89% [71.57%, 77.39%]** | **84.07% [79.78%, 88.00%]** | 65.67% | 6.08% | 19.82 | 85.18% |
| | Linear (Logistic Regression) [Pure NumPy] | 57.76% [55.95%, 59.40%] | 67.54% | **67.81%** | **4.39%** | **14.45** | 85.33% |
| | Persistence Baseline | 73.49% [70.20%, 76.22%] | 76.41% | 67.44% | 5.10% | 16.64 | **85.50%** |
| | Rainfall Threshold Rule | 46.26% [43.07%, 49.39%] | 93.55% | 30.89% | 28.08% | 94.36 | 60.22% |
| **t + 3d (72h)** | **LightGBM (Primary)** | **67.74% [64.52%, 70.35%]** | **77.62% [72.75%, 82.23%]** | 57.98% | 7.73% | 25.36 | 81.25% |
| | Linear (Logistic Regression) [Pure NumPy] | 55.11% [53.34%, 56.74%] | 64.31% | **63.29%** | **5.13%** | **16.82** | **82.49%** |
| | Persistence Baseline | 64.79% [61.64%, 67.76%] | 68.35% | 58.35% | 6.71% | 22.00 | 80.97% |
| | Rainfall Threshold Rule | 43.19% [40.32%, 46.07%] | 88.31% | 28.53% | 29.47% | 99.45 | 57.54% |

*Note on 95% Confidence Intervals*: 7-day block bootstrap resamples (1,000 iterations) show overlapping CIs between LightGBM and Persistence on 1d Macro F1 (Persistence [82.7%, 86.8%] vs LightGBM [81.1%, 85.5%]). However, LightGBM achieves superior High-Risk Recall at 1d (90.93% vs 86.90%) and outperforms Persistence across both Macro F1 and Recall at 2d and 3d horizons.

*Note on Leave-One-RIVER-Out (LORO)*: Stations located on the same river (e.g. `KL-PER-01` and `KL-PER-02`) share basin discharge dynamics ($r > 0.90$). Standard cross-validation across stations in the same basin overestimates spatial generalization. Leave-One-RIVER-Out (LORO) provides a strict out-of-basin spatial generalization evaluation.

---

## 5. Scientific Limitations & Data Honesty

1. **GloFAS Modeled Discharge**: River discharge ($m^3/s$) is derived from Open-Meteo GloFAS reanalysis modeling, NOT physical river gauge height meters.
2. **Observed Past Rainfall Only**: Model features use historical observed past rainfall, NOT future numerical weather forecast predictions.
3. **Percentile Risk Proxies**: Danger thresholds are station-specific historical training period discharge percentiles (p90=Yellow, p97=Orange, p99.5=Red), NOT official CWC stage levels.
4. **Max Horizon Cap**: Prediction lead times are strictly capped at the 3-day ($t+3\text{d}$) maximum horizon. GloFAS discharge updates daily.
5. **Rating Curve Rating Approximation**: Sensor water level stage ($h$) is converted to discharge ($Q$) via a documented rating curve equation ($Q = a \cdot (h - h_0)^b$).

---

## 6. Open Hardware Roadmap & Wokwi Simulation

*Note: There is NO physical hardware deployed in this round. The system operates via a software virtual sensor layer. The hardware blueprint below is planned for future physical field deployment.*

- **Firmware Stub**: `/firmware-stub/node_firmware.ino` (ESP32 C++ sketch using JSN-SR04T ultrasonic transducer & tipping bucket rain gauge).
- **PlatformIO Config**: `/firmware-stub/platformio.ini` & `.github/workflows/firmware.yml`.
- **Wokwi Browser Diagram**: `/wokwi/diagram.json` & `/wokwi/README.md`.
- **Bill of Materials**: Target BOM cost: ₹3,990 INR / ~$48 USD per node.

---

## 7. Why Not Just Use GloFAS Directly?

Global systems like GloFAS are indispensable, but they are not designed to be end-to-end local early-warning platforms for municipal emergency managers. FloodSense builds on top of GloFAS to address critical operational gaps:
1. **Resolution & Local Geometry**: GloFAS provides global 0.1° (~10km) discharge reanalysis updated once daily. Local river basins (such as the Periyar or Jia Bharali) require hyper-local telemetry, station-level thresholding, and sub-hourly alerting.
2. **Actionable Risk Translation**: GloFAS outputs coarse volumetric discharge ($m^3/s$). FloodSense translates discharge and rainfall into clear local risk states (Green/Yellow/Orange/Red), plain-language driver explanations, and automated local evacuation route links.
3. **Alert Flapping & Hysteresis Control**: Raw threshold alerts fluctuate rapidly near danger marks. FloodSense enforces a state-machine hysteresis engine to prevent alert fatigue among emergency responders.
4. **Hardware & Offline Resiliency**: FloodSense integrates directly with low-cost ESP32 field telemetry nodes, works 100% offline using bundled local datasets, and dispatches localized multilingual alerts (English, Hindi, Malayalam, Assamese) via Telegram and in-app outbox.

---

## 8. License & Credits

- **License**: [MIT License](LICENSE)
- **Built for**: FOSSEE Open Hardware National Make-A-Thon 2026 (Disaster Detection & Early Warnings: Floods Monitoring)
- **Data Sources**: Open-Meteo Weather & GloFAS Global Flood APIs / geoBoundaries State Geometry.

