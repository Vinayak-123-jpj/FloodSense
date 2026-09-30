# FloodSense — Software-Only Flood Early-Warning Platform
## FOSSEE Open Hardware National Make-A-Thon 2026 (Disaster Detection & Early Warnings: Floods Monitoring)

---

### 1. Architecture Overview

FloodSense is designed as a software-only digital twin and early-warning platform that mirrors a real-world IoT sensor grid for flood monitoring. The system receives high-frequency telemetry from virtual sensor nodes (simulating ESP32 hardware nodes over HTTP/WebSocket), ingests hydrological and meteorological data (Open-Meteo Weather & River Discharge APIs), computes multi-horizon flood risk using a LightGBM/GradientBoosting machine learning pipeline, and broadcasts localized alerts with Hindi/English support and OSRM evacuation routes.

```mermaid
graph TD
    subgraph Virtual Sensor Layer & External Data
        VS[Sensor Simulator / ESP32 Firmware Stub] -->|HTTP POST /api/readings| API[FastAPI Backend]
        OM[Open-Meteo APIs / Bundled Offline CSVs] -->|Data Fetcher| DB[(SQLite Database)]
    end

    subgraph Backend Core & Risk Engine
        API -->|Readings & Telemetry| DB
        SCHED[APScheduler Background Jobs] -->|Tick Simulation & Weather Update| API
        ML[ML Risk Engine / Fallback Rules] -->|Predict Risk Levels| DB
        ALERT[Alert Engine & Deduplicator] -->|Generate Alerts| BOT[Telegram Bot / In-App Outbox]
    end

    subgraph Real-Time Communication
        API -->|WebSocket /ws/live| WS[Live Telemetry Stream]
    end

    subgraph Single-Page Frontend Application (React + Vite + TS)
        FE[React Frontend] -->|REST Calls| API
        FE -->|Live WS Subscriptions| WS
        FE -->|Leaflet Maps| MAP[Interactive Atlas & Risk Polygons]
        FE -->|Recharts & Visx| CHARTS[Hydrological Trends & Forecast Band]
        FE -->|Scenario Replay| REPLAY[Kerala 2018 & Assam Historical Scrubbers]
    end
```

---

### 2. Workspace Directory & File Structure

```
floodsense/
├── PLAN.md                         # Architecture, design system & phase checklist
├── README.md                       # Main pitch, quickstart, docs links, model metrics
├── LICENSE                         # MIT License
├── docker-compose.yml              # Single command orchestration
├── Dockerfile.backend              # Python 3.11 FastAPI service container
├── Dockerfile.frontend             # React + Vite static build & Nginx container
├── requirements.txt                # Python backend dependencies
├── package.json                    # Node.js frontend dependencies
├── pytest.ini                      # Test runner configuration
├── .env.example                    # Environment settings (Telegram token, DB URL, etc.)
│
├── backend/                        # FastAPI Backend Application
│   ├── main.py                     # Entrypoint & Lifespan handler
│   ├── config.py                   # Environment & Application settings
│   ├── database.py                 # SQLAlchemy engine & session setup
│   ├── models.py                   # SQLAlchemy ORM models (Station, Reading, Alert)
│   ├── schemas.py                  # Pydantic schemas for request/response validation
│   ├── seed.py                     # Database seeder with bundled historical CSVs
│   ├── sensor_simulator.py         # Node simulator (noise, dropouts, battery drain)
│   ├── api/
│   │   ├── stations.py             # GET /api/stations, GET /api/stations/{id}
│   │   ├── readings.py             # POST /api/readings, GET /api/stations/{id}/readings
│   │   ├── forecast.py             # GET /api/stations/{id}/forecast
│   │   ├── alerts.py               # GET /api/alerts, POST /api/alerts/clear
│   │   ├── simulate.py             # POST /api/simulate/start|stop|speed
│   │   ├── health.py               # GET /api/health
│   │   └── websocket.py            # WebSocket /ws/live broadcast manager
│   ├── ml/
│   │   ├── feature_engineering.py  # 6h/24h/72h rainfall sums, discharge rate of change
│   │   ├── train.py                # ML pipeline training script (time-based split)
│   │   ├── predictor.py            # Model inference & rule-based fallback engine
│   │   └── explainability.py       # Plain-language top-3 risk driver calculator
│   └── alerts/
│       ├── alert_engine.py         # Hysteresis, deduplication & state tracking
│       ├── telegram_bot.py         # Multilingual Telegram Bot (/start, /status, /lang)
│       └── evacuation.py           # OSRM public route generator to high ground
│
├── frontend/                       # React 18 + Vite + TypeScript Frontend
│   ├── index.html                  # Main HTML entrypoint with font imports
│   ├── vite.config.ts              # Vite configuration
│   ├── tailwind.config.js          # Custom theme colors (Day Survey / Night Watch)
│   ├── src/
│   │   ├── main.tsx                # App entrypoint
│   │   ├── App.tsx                 # Router & Layout wrapper
│   │   ├── types/                  # TypeScript interfaces (Station, Reading, Alert, Risk)
│   │   ├── theme/                  # ThemeContext (Light/Dark mode & contours)
│   │   ├── services/               # API client (Axios/Fetch) & WebSocket manager
│   │   ├── components/
│   │   │   ├── common/             # Header, Navigation, StatCard, Badge, Skeleton, Clock
│   │   │   ├── map/                # Leaflet map, SVG markers, Topo polygons, Cursor readout
│   │   │   ├── charts/             # Hydrological gauge, 72h discharge & forecast band
│   │   │   ├── stations/           # Station detail sidebar, battery/signal health
│   │   │   ├── replay/             # Scrubber controls, speed selector, What-if rain slider
│   │   │   └── alerts/             # Alert Outbox list, Telegram English/Hindi preview
│   │   └── pages/
│   │       ├── LandingPage.tsx     # Hero with live map centerpiece & quick stats
│   │       ├── LiveMonitorPage.tsx # Full-height map + side panel + live event timeline
│   │       ├── ScenarioReplayPage.tsx # Historical scrubber (Kerala 2018 & Assam) + What-if
│   │       ├── AlertsPage.tsx      # Outbox, history, and Telegram message preview
│   │       ├── ModelMethodPage.tsx # Model performance, confusion matrix, baseline metrics
│   │       └── OpenHardwarePage.tsx# Firmware sketch, wiring diagram, BOM & roadmap
│
├── firmware-stub/                  # Open Hardware Blueprint & Stub
│   ├── node_firmware.ino           # ESP32 Arduino sketch stub (HTTP POST to /api/readings)
│   ├── wiring_diagram.svg          # SVG schematic of ESP32 + Ultrasonic + Rain gauge + Solar
│   └── bom.md                      # Complete Bill of Materials with estimated costs in INR
│
├── data/                           # Data Storage & Offline Fallback Files
│   ├── raw/                        # Open-Meteo cached CSVs (Rainfall & River Discharge)
│   ├── processed/                  # Feature-engineered CSVs for ML training
│   └── stations_metadata.json      # Metadata for Kerala (6) and Assam (5) stations
│
├── models/                         # Serialized ML Models
│   ├── flood_risk_model.joblib     # Trained LightGBM / GradientBoosting classifier
│   └── feature_scaler.joblib       # Standard Scaler for feature normalization
│
├── reports/                        # Model Evaluation & Backtest Reports
│   ├── model_report.md             # Comprehensive metrics, confusion matrix & backtest
│   ├── confusion_matrix.png        # Rendered confusion matrix visualization
│   ├── feature_importance.png      # Feature importance chart
│   └── kerala_2018_backtest.png    # Backtest lead-time chart for Kerala 2018 event
│
├── docs/                           # Project Documentation
│   ├── architecture.md             # In-depth architectural design & data flow
│   ├── data_sources.md             # Open-Meteo & elevation dataset specifications
│   ├── model_card.md               # Standardized ML Model Card
│   └── hardware_ready_design.md    # Hardware integration guide & ESP32 specification
│
├── scripts/
│   ├── fetch_data.py               # Open-Meteo downloader & offline CSV cache generator
│   ├── train_model.py              # CLI trigger to train and evaluate ML model
│   └── record_demo.md              # Scene-by-scene 3-minute video walkthrough script
│
└── tests/                          # Automated Pytest Suite
    ├── test_api.py                 # REST & WebSocket endpoint tests
    ├── test_simulator.py           # Sensor simulator noise and payload tests
    ├── test_ml.py                  # Predictor and rule-based fallback tests
    └── test_alerts.py              # Alert engine hysteresis & deduplication tests
```

---

### 3. Focus Regions & Virtual Station Definitions

#### Primary Region: Kerala (August 2018 Historic Floods)
1. **Neeleswaram (Periyar River)**: Lat `10.1416`, Lng `76.5781`, Warning `4.5m`, Danger `6.0m`, Elevation `12m`.
2. **Aluva (Periyar River Downstream)**: Lat `10.1076`, Lng `76.3516`, Warning `3.8m`, Danger `5.2m`, Elevation `7m`.
3. **Chengannur (Pamba River)**: Lat `9.3175`, Lng `76.6122`, Warning `5.0m`, Danger `6.5m`, Elevation `9m`.
4. **Muvattupuzha (Muvattupuzha River)**: Lat `9.9813`, Lng `76.5772`, Warning `4.0m`, Danger `5.5m`, Elevation `14m`.
5. **Chalakudy (Chalakudy River)**: Lat `10.3070`, Lng `76.3323`, Warning `4.2m`, Danger `5.8m`, Elevation `11m`.
6. **Thumpamon (Achenkovil River)**: Lat `9.2560`, Lng `76.7110`, Warning `4.8m`, Danger `6.2m`, Elevation `15m`.

#### Secondary Region: Assam (Brahmaputra Basin)
1. **Guwahati (Brahmaputra River)**: Lat `26.1833`, Lng `91.7500`, Warning `48.5m`, Danger `49.68m`, Elevation `52m`.
2. **Dibrugarh (Brahmaputra Upper Basin)**: Lat `27.4728`, Lng `94.9120`, Warning `104.5m`, Danger `105.7m`, Elevation `108m`.
3. **Kampur (Kopili River)**: Lat `26.1500`, Lng `92.5833`, Warning `59.0m`, Danger `60.5m`, Elevation `63m`.
4. **NH37 Crossing (Dhansiri River)**: Lat `26.5667`, Lng `93.7333`, Warning `78.0m`, Danger `79.5m`, Elevation `82m`.
5. **Jia Bharali (Tezpur)**: Lat `26.6333`, Lng `92.8000`, Warning `76.5m`, Danger `77.5m`, Elevation `80m`.

---

### 4. Data Sources & Offline Fallback Strategy

1. **Meteorological Data**: Open-Meteo Historical Weather API (hourly precipitation `precipitation` in mm/hr).
2. **Hydrological Data**: Open-Meteo Global Flood API (daily river discharge `river_discharge` in m³/s).
3. **Granularity Alignment**: Since river discharge data is daily and rainfall is hourly, our prediction horizon is calibrated for **24h to 72h early warning lead times**.
4. **Offline Resilience**:
   - `scripts/fetch_data.py` queries Open-Meteo APIs for the historical date ranges (Kerala 2018 & Assam 2020-2024).
   - Saved into `/data/raw/kerala_weather_flood.csv` and `/data/raw/assam_weather_flood.csv`.
   - All backend APIs, ML pipelines, and simulator components fall back to reading these committed CSV files when an external network request fails or when running offline.

---

### 5. UI/UX Design System: "Hydrological Survey Atlas"

#### Color Palette
- **Light Theme ("Day Survey")**:
  - Background: `#F2EEE4` (Warm vintage paper)
  - Surface Card: `#FAF7F0` (Light parchment)
  - Primary Text / Ink: `#14202B` (Deep navy ink)
  - Secondary Text: `#4A5568` (Muted slate)
  - Accent / River Teal: `#1F6B75` (Field survey teal)
  - Ochre / Highlight: `#C88A2E` (Topographic gold)
  - Border Lines: `1px solid #D8D2C2` (Crisp technical rules)

- **Dark Theme ("Night Watch")**:
  - Background: `#0C141B` (Deep nocturnal slate)
  - Surface Card: `#131E28` (Dark survey card)
  - Primary Text: `#E6E1D5` (Soft paper white)
  - Accent / River Teal: `#2B8C98` (Brightened survey teal)

- **Risk Levels (Color-blind Safe + Dual-Coded with Icons/Shapes)**:
  - **Green (Normal)**: `#2E7D32` (Sage Green) + `[CIRCLE]` icon
  - **Yellow (Advisory)**: `#D97706` (Warm Amber) + `[TRIANGLE]` icon
  - **Orange (Warning)**: `#EA580C` (Burnt Orange) + `[DIAMOND]` icon
  - **Red (Danger)**: `#DC2626` (Signal Red) + `[OCTAGON]` icon

#### Typography
- **Headings**: Editorial Serif (`Fraunces` / `Newsreader` / fallback `serif`)
- **Body UI**: Clean Grotesk (`Inter Tight` / `Instrument Sans` / `sans-serif`)
- **Metrics, Coordinates & Timestamps**: Monospace (`JetBrains Mono` / `IBM Plex Mono` / `monospace`)

---

### 6. Phase Implementation Plan & Verification Strategy

#### Phase 1: Backend Core & Virtual Sensor Layer
- Build SQLAlchemy models, Pydantic schemas, and SQLite database.
- Implement REST endpoints: `/api/readings`, `/api/stations`, `/api/stations/{id}/readings`, `/api/stations/{id}/forecast`, `/api/alerts`, `/api/simulate/start|stop|speed`, `/api/health`.
- Implement WebSocket `/ws/live` stream.
- Write `sensor_simulator.py` supporting standalone execution and background APScheduler execution.
- Create `/firmware-stub/` (`node_firmware.ino`, `wiring_diagram.svg`, `bom.md`).
- **Verification**: Run `pytest tests/test_api.py` and `pytest tests/test_simulator.py`.

#### Phase 2: ML Risk Engine & Explainability
- Implement feature engineering (6h, 24h, 72h rolling precipitation, discharge rate of change, antecedent wetness proxy).
- Train LightGBM / GradientBoosting model on time-based splits.
- Build explainability engine (top-3 plain-language risk factors).
- Build rule-based fallback risk classifier.
- Generate `/reports/model_report.md` and charts.
- **Verification**: Run `python scripts/train_model.py` and `pytest tests/test_ml.py`.

#### Phase 3: Alert Engine & Multilingual Bot
- Build alert engine with hysteresis & deduplication.
- Build Telegram Bot integration (English & Hindi support).
- Build OSRM evacuation route link generator to higher elevation.
- Expose Alert Outbox API.
- **Verification**: Run `pytest tests/test_alerts.py`.

#### Phase 4: Frontend ("Hydrological Survey Atlas")
- Set up React + Vite + TypeScript + Tailwind CSS design system.
- Build custom desaturated Leaflet map with low-lying zone polygons & pulsed risk markers.
- Implement Landing Page, Live Monitor Page, Scenario Replay Page (with What-If slider), Alerts Page, Model & Method Page, and Open Hardware Page.
- Add Theme toggle (Day Survey / Night Watch) with smooth Framer Motion transitions.
- **Verification**: Run frontend build (`npm run build`) and test all interactive flows in browser.

#### Phase 5: Packaging & Final Submission Polish
- Write `docker-compose.yml`, `Dockerfile.backend`, `Dockerfile.frontend`.
- Write `README.md` with pitch, Mermaid diagram, setup instructions, metrics, limitations, hardware roadmap.
- Write `/docs/` documents (`architecture.md`, `data_sources.md`, `model_card.md`, `hardware_ready_design.md`).
- Write `scripts/record_demo.md`.
- Conduct full end-to-end self-audit from clean build.
- **Verification**: Execute `docker compose up --build` and verify full system end-to-end.

---
