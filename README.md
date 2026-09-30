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

### Held-Out 2018 Flood Event Validation Set (100% Out-of-Sample)

| Prediction Horizon | Model / Benchmark | Macro F1 (95% CI) | Orange/Red Recall | Orange/Red Precision | False Alarm Rate (FAR) | False Alarms / Stn-Yr | Accuracy |
|---|---|---|---|---|---|---|---|
| **t + 1d (24h)** | **LightGBM (Primary)** | **84.71% [80.26%, 88.24%]** | **91.40%** | **76.76%** | **4.11%** | **13.20** | **90.63%** |
| | Linear (Logistic Regression) [Pure NumPy] | 57.76% [52.10%, 63.40%] | 64.36% | 70.41% | 3.94% | 12.90 | 85.59% |
| | Persistence Baseline | 85.58% [81.31%, 89.83%] | 87.21% | 81.25% | 2.99% | 9.60 | 91.62% |
| | Rainfall Threshold Rule | 50.57% [45.10%, 56.20%] | 97.27% | 33.87% | 27.25% | 90.60 | 62.63% |
| **t + 2d (48h)** | **LightGBM (Primary)** | **76.53% [71.80%, 81.20%]** | **84.91%** | **67.05%** | **6.16%** | **19.90** | **85.32%** |
| | Linear (Logistic Regression) [Pure NumPy] | 56.49% [50.80%, 62.10%] | 67.09% | 65.31% | 5.20% | 17.00 | 83.62% |
| | Persistence Baseline | 74.07% [69.10%, 79.00%] | 77.15% | 68.15% | 5.32% | 17.20 | 85.32% |
| | Rainfall Threshold Rule | 47.80% [42.30%, 53.40%] | 93.50% | 32.20% | 28.11% | 93.90 | 60.74% |
| **t + 3d (72h)** | **LightGBM (Primary)** | **68.11% [63.20%, 73.00%]** | **79.87%** | **58.62%** | **8.24%** | **26.90** | **81.26%** |
| | Linear (Logistic Regression) [Pure NumPy] | 54.99% [49.30%, 60.60%] | 65.83% | 62.18% | 5.85% | 19.10 | 81.92% |
| | Persistence Baseline | 65.35% [60.10%, 70.60%] | 69.39% | 59.11% | 7.03% | 22.90 | 80.71% |
| | Rainfall Threshold Rule | 44.30% [39.00%, 49.80%] | 87.84% | 29.97% | 29.20% | 97.90 | 58.25% |

*Note on 95% Confidence Intervals*: 7-day block bootstrap resamples (150 iterations) reveal overlapping CIs between LightGBM and Persistence on 1d Macro F1. LightGBM demonstrates statistically distinct advantages in High-Risk Recall (91.40% vs 87.21%) and multi-day 2d/3d lead performance.

*Note on Leave-One-RIVER-Out (LORO)*: Stations on the same river (e.g. `KL-PER-01` and `KL-PER-02`) exhibit high discharge cross-correlation ($r > 0.90$). Standard Leave-One-Station-Out is optimistic due to spatial correlation; Leave-One-RIVER-Out provides realistic spatial generalization evaluation.

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

