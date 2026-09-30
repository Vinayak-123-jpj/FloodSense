# FloodSense — Software-Only Flood Early-Warning Platform
### FOSSEE Open Hardware National Make-A-Thon 2026 (Disaster Detection & Early Warnings: Floods Monitoring)

[![Licence: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11](https://img.shields.io/badge/Python-3.11-teal.svg)](backend/)
[![React: 18](https://img.shields.io/badge/React-18-61dafb.svg)](frontend/)
[![Held-Out Accuracy: 90.63%](https://img.shields.io/badge/HeldOut_2018_Accuracy-90.63%25-success.svg)](reports/metrics.json)

**FloodSense** is a software-only flood early-warning digital twin platform that emulates physical IoT sensor grids to deliver 24-to-72-hour early warning predictions across river catchments in Kerala and Assam. Powered by a FastAPI backend, a leakage-audited LightGBM machine learning classifier trained on 131,490 daily GloFAS records (1990–2025), and a desaturated "Hydrological Survey Atlas" React frontend, FloodSense features hysteresis alert deduplication, multilingual Telegram warnings (English & Hindi), OpenStreetMap evacuation routing, and an open-hardware ESP32 blueprint.

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
git clone https://github.com/floodsense/floodsense.git
cd floodsense

# 2. Launch complete platform with single command
docker compose up --build
```

- **Frontend Application**: `http://localhost:3000`
- **FastAPI OpenAPI Documentation**: `http://localhost:8000/docs`
- **Backend Health Diagnostics**: `http://localhost:8000/api/health`

---

## 3. Machine Learning Audit & Performance Summary

- **Prediction Task**: Multi-Horizon Risk Level Classification ($t+1\text{d}, t+2\text{d}, t+3\text{d}$)
- **Dataset**: 131,490 Daily Hydrological Rows (1990–2025 across 10 stations in Kerala & Assam)
- **Data Leakage Audit**: **PASSED**. Strict 7-day chronological split gap and held-out 2018 validation protocol.
- **Held-Out 2018 Test Accuracy**: **90.63%**
- **Held-Out 2018 Macro F1-Score**: **84.71%** (vs Persistence F1: 85.58%)
- **Orange/Red High-Risk Recall**: **91.40%**
- **False Alarm Rate (Orange/Red Alerts)**: **4.11%**
- **August 2018 Warning Lead Time**: Median of **2 Days (48 Hours)** prior to peak deluge across Kerala gauging stations.

*Full model metrics, confusion matrix, feature importances, and dynamic JSON metrics are available in [`reports/model_report.md`](reports/model_report.md) and [`reports/metrics.json`](reports/metrics.json).*

---

## 4. System Limitations & Honesty

1. **Daily vs Hourly Granularity**: Open-Meteo Flood API provides **daily** river discharge, whereas precipitation is **hourly**. Micro-burst flash floods under 3 hours rely heavily on the `rain_sum_6h` feature until daily discharge updates.
2. **Dam Release Anomaly**: Natural river hydraulics are assumed. Unannounced upstream dam gate releases without rain correlation can cause delayed predictions.

---

## 5. Open Hardware Deployment Roadmap

While sensors are simulated this round, FloodSense includes an open-hardware blueprint in `/firmware-stub/`:
- **`node_firmware.ino`**: ESP32 C++ Arduino sketch using JSN-SR04T ultrasonic transducer & tipping bucket rain gauge.
- **`wiring_diagram.svg`**: Vector wiring schematic.
- **`bom.md`**: Bill of Materials (INR ₹3,990 per node, ~$48 USD).

---

## 6. License & Credits

- **License**: [MIT License](LICENSE)
- **Built for**: FOSSEE Open Hardware National Make-A-Thon 2026 (Disaster Detection & Early Warnings: Floods Monitoring)
- **Data Sources**: Open-Meteo Weather & Global Flood APIs.
