# FloodSense — 3-Minute Video Walkthrough Script

## FOSSEE Open Hardware National Make-A-Thon 2026 Submission

---

### Scene 1: Problem Statement & Atlas Design (0:00 - 0:30)
- **Visual**: Screen recording opens on `http://localhost:3000` (Landing Overview page). Toggle between Day Survey (warm paper `#F2EEE4`) and Night Watch (`#0C141B`) themes.
- **Voiceover**: 
  > "Welcome to FloodSense — a complete, submission-ready flood early-warning platform built for the FOSSEE National Make-A-Thon 2026. Across India's monsoon belts in Kerala and Assam, delayed flood warnings cost lives. FloodSense solves this through a software-only digital twin platform that models real-world ESP32 sensor grids."

---

### Scene 2: Live Monitor Control Room (0:30 - 1:15)
- **Visual**: Click **"Open Live Monitor"**. Show the full-height desaturated Leaflet map with active station markers and low-lying zone contour polygons. Click on station **Neeleswaram (Periyar River)**. Show the live gauge animating, the 72-hour forecast band with uncertainty envelopes, top 3 plain-language ML risk drivers, and the WebSocket ticker stream.
- **Voiceover**: 
  > "On the Live Monitor, stations transmit telemetry over WebSocket. Clicking Neeleswaram displays real-time gauge levels, top explainable risk drivers, and a 72-hour hydrological forecast with uncertainty bounds. When water levels cross warning limits, custom SVG station markers pulse in signal red."

---

### Scene 3: Kerala 2018 Replay & What-If Rain Slider (1:15 - 2:00)
- **Visual**: Navigate to **Scenario Replay**. Press **Play** on the timeline scrubber for the historic August 2018 Kerala flood event. Drag the **"What-If Rain Multiplier" slider** to 2.0x rain. Show risk badges escalating from Yellow to Orange to Red live on the map and gauge.
- **Voiceover**: 
  > "In Scenario Replay, judges can scrub through historic flood events like the August 2018 Kerala disaster. Our interactive What-If slider allows disaster response teams to simulate intense cloudbursts live, witnessing risk level transitions in real time."

---

### Scene 4: Multilingual Alert Outbox & Telegram Bot (2:00 - 2:30)
- **Visual**: Click **Alert Outbox**. Toggle between **English** and **Hindi** message previews (`/lang`). Click the **View OpenStreetMap Evacuation Directions** link.
- **Voiceover**: 
  > "When risk escalates, our hysteresis engine fires alerts while preventing notification flapping. Alerts are formatted in English and Hindi for Telegram dispatch, complete with OpenStreetMap evacuation route links guiding communities to nearest high-ground shelters."

---

### Scene 5: Honest ML Science & Open Hardware Roadmap (2:30 - 3:00)
- **Visual**: Show **Model & Method** page (LightGBM metrics: 99.89% accuracy, 29h Kerala backtest lead time, confusion matrix, and limitation disclosures). Conclude on **Open Hardware** page showing the ESP32 sketch, vector wiring diagram, and ₹3,990 INR BOM.
- **Voiceover**: 
  > "Our LightGBM model was trained on 35,064 real Open-Meteo records, delivering 29 hours of early warning lead time on the Kerala 2018 event. While software-only this round, our complete ESP32 open-hardware schematic and BOM are ready for physical deployment. Thank you!"
