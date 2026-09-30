# FloodSense Technical Architecture & Data Flow

## FOSSEE Open Hardware National Make-A-Thon 2026

---

### 1. High-Level Architectural Overview

FloodSense is engineered as a software-only early warning digital twin platform designed to mirror real-world IoT sensor networks.

```mermaid
graph TD
    subgraph Layer 1: Virtual Sensors & Open Data
        VS[Sensor Emulator / ESP32 Firmware Stub] -->|HTTP POST /api/readings| API[FastAPI Backend Core]
        OM[Open-Meteo Weather & Flood APIs / Offline CSVs] -->|Data Fetcher| DB[(SQLite Database)]
    end

    subgraph Layer 2: Ingestion & ML Risk Pipeline
        API -->|Raw Telemetry| FE[Feature Engineering Module]
        FE -->|6h, 24h, 72h Rain & Discharge| ML[LightGBM Risk Classifier]
        ML -->|Predict Green/Yellow/Orange/Red| EXP[Explainability Engine]
    end

    subgraph Layer 3: Multilingual Alerts & Route Generator
        ML -->|Risk Escalation| HYST[Hysteresis & Deduplication Engine]
        HYST -->|Generate Evacuation Link| OSRM[OSRM Routing Service]
        HYST -->|Deliver Multilingual Message| BOT[Telegram Bot / Alert Outbox]
    </div>

    subgraph Layer 4: Hydrological Survey Atlas UI
        API -->|REST & WebSocket /ws/live| FE_APP[React + Vite + TypeScript Frontend]
        FE_APP -->|Desaturated Map| MAP[Leaflet Contour Atlas]
        FE_APP -->|72h Forecast Band| CHART[Recharts Hydrological Trends]
        FE_APP -->|Replay Scrubber| REPLAY[Kerala 2018 & Assam Historical Replay]
    end
```

---

### 2. Microservice Component Specifications

#### A. FastAPI Ingestion Server (`backend/main.py`)
- High-performance asynchronous ASGI Web Framework.
- Lifespan startup handler seeds station metadata from `data/stations_metadata.json` and launches APScheduler background simulator job.
- OpenAPI 3.0 document auto-generated at `/docs`.

#### B. Virtual Sensor Node Emulator (`backend/sensor_simulator.py`)
- Emulates 11 monitoring stations across Kerala (6) and Assam (5).
- Injects physical noise models:
  - Gaussian water level distance measurement noise ($\sigma = 1.5 \text{ cm}$)
  - Solar battery charge/discharge cycles ($85\% - 100\%$)
  - Cellular RSSI signal fading ($-55 \text{ dBm to } -110 \text{ dBm}$)
  - Intermittent packet dropouts ($2\%$ loss rate)
  - Sensor fault simulation

#### C. Machine Learning Risk Classifier (`backend/ml/predictor.py`)
- Primary Algorithm: LightGBM Multi-class Classifier.
- Ingests 8 hydrological features: `rain_sum_6h`, `rain_sum_24h`, `rain_sum_72h`, `discharge_m3s`, `discharge_rate_of_change_24h`, `antecedent_wetness_index`, `month`, `day_of_year`.
- Features physical safety override rules for extreme danger levels.

#### D. Hysteresis & Outbox Alert Engine (`backend/alerts/alert_engine.py`)
- Risk Escalations (e.g. Yellow -> Orange) trigger notifications immediately.
- Risk Downgrades (e.g. Orange -> Yellow) enforce a **2-tick hysteresis delay** to eliminate alert flapping.
- Generates OpenStreetMap evacuation links to nearest high-ground shelters.
- Formats messages in English and Hindi (`/lang` toggle).
