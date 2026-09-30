# FloodSense — 3-Minute Video Demonstration Script

**Target Video Duration**: 3 Minutes (180 Seconds)  
**Theme**: FOSSEE Open Hardware National Make-A-Thon 2026 (Disaster Detection & Early Warnings: Floods Monitoring)

---

## Scene Breakdown & Voiceover Guide

### Scene 1: Introduction & System Architecture (0:00 - 0:35)
- **Visual**: Open `http://localhost:3000` (Landing Page). Show the hero section, active river gauging atlas, and click the "Guided Demo Tour" button.
- **Voiceover**:
  > "Welcome to FloodSense, a software-only flood early-warning platform built for the FOSSEE Open Hardware National Make-A-Thon 2026. FloodSense addresses severe flood risks across river basins in Kerala and Assam by combining virtual IoT sensor digital twins, 36-year daily GloFAS river discharge reanalysis data from 1990 to 2025, and a leakage-audited LightGBM multi-horizon classifier."

---

### Scene 2: Live Monitor Control Room & Virtual Telemetry (0:35 - 1:10)
- **Visual**: Navigate to `/live` (Live Monitor). Show station markers on the desaturated OpenTopoMap Leaflet map, click Neeleswaram station (`KL-PER-01`), show the live ticker stream `/ws/live`, the `[SIMULATED NODE]` badge, and the explainable ML top-3 drivers.
- **Voiceover**:
  > "In live mode, FloodSense receives HTTP and WebSocket telemetry payloads from virtual ESP32 sensor nodes emulating ultrasonic water level sensors, rain gauges, solar battery drain, and signal RSSI. Water level stage is converted to river discharge via a documented rating curve ($Q = a \cdot (h - h_0)^b$). Notice how the explainable AI module highlights top risk drivers in plain language."

---

### Scene 3: Historical Event Replay & What-If Stress Testing (1:10 - 1:45)
- **Visual**: Navigate to `/replay` (Scenario Replay). Click Play on the Kerala August 2018 scrubber (replay starts instantly within 2 seconds). Move the What-If Rainfall Multiplier slider to 2.0x.
- **Voiceover**:
  > "Next, we open the Disaster Replay simulator. Here, we scrub through the catastrophic August 2018 Kerala flood event evaluated on our out-of-sample held-out 2018 model. Watch the water level gauge transition smoothly from Green to Yellow, Orange, and Red. Adjusting the What-If rainfall slider lets emergency response teams stress-test catchment response under extreme deluge conditions."

---

### Scene 4: Multilingual Alert Engine & Evacuation Routing (1:45 - 2:15)
- **Visual**: Navigate to `/alerts` (Alert Outbox). Toggle between English, Hindi, Malayalam, and Assamese alert messages. Click "View Evacuation Route" on an active Red alert to reveal the OpenStreetMap route to the nearest high-ground relief shelter.
- **Voiceover**:
  > "When river levels breach thresholds, the hysteresis alert engine fires deduplicated notifications, preventing alarm fatigue caused by noisy sensor readings. Outbox messages are instantly formatted in English, Hindi, Malayalam, and Assamese, complete with direct OpenStreetMap navigation routes to designated high-elevation evacuation shelters."

---

### Scene 5: Data Science Audit & Baseline Honesty Segment (2:15 - 2:45)
- **Visual**: Navigate to `/model` (Model & Method Page). Show the top metric cards (Macro F1: 84.71%, High-Risk Recall: 91.40%, Lead Time: 2 Days), the multi-horizon baseline comparison table, 95% bootstrap CIs, LORO validation, and the per-station 2018 breakdown table.
- **Voiceover**:
  > "Now for our Data Science Audit. In the spirit of scientific transparency: river discharge is GloFAS reanalysis modeled data, thresholds are percentile proxies, and lead times are capped at our 3-day maximum horizon. On our held-out 2018 test set, LightGBM achieves 84.71% Macro F1 at 24 hours (95% CI: [80.26%, 88.24%]) and 91.40% recall on severe Orange/Red alert days. While 1-day Macro F1 overlaps with Persistence, LightGBM yields higher high-risk recall and distinct gains at 2-day and 3-day lead horizons."

---

### Scene 6: Conclusion & Open Hardware Roadmap (2:45 - 3:00)
- **Visual**: Return to Landing Page or README. Show the Docker Compose quickstart and open hardware ESP32 blueprint (`/firmware-stub/`).
- **Voiceover**:
  > "FloodSense is fully containerized and runs with a single command (`docker compose up --build`). While hardware is simulated this round, our complete solar-autonomous ESP32 firmware and ₹3,990 INR BOM are ready for physical deployment. Thank you."
