# Wokwi ESP32 Browser Simulation Guide

> [!IMPORTANT]
> **SIMULATION ONLY — NO PHYSICAL HARDWARE DEPLOYED THIS ROUND**
> 
> Per National Make-A-Thon 2026 rules, Round 1 is software-only. This Wokwi diagram and firmware stub demonstrate hardware readiness for physical deployment in Round 2.

## Quick Start (Browser Simulation)

1. Open [https://wokwi.com/projects/new/esp32](https://wokwi.com/projects/new/esp32).
2. Replace `sketch.ino` with the contents of [`firmware-stub/node_firmware.ino`](../firmware-stub/node_firmware.ino).
3. Replace `diagram.json` with the contents of [`wokwi/diagram.json`](diagram.json).
4. Click **Start Simulation** (Play button).
5. Interact with simulated sensors:
   - **HC-SR04 Ultrasonic Sensor**: Click sensor to adjust distance slider (simulates river water level).
   - **Pushbutton**: Click to simulate tipping bucket rain gauge pulse (0.28mm rain per pulse).
   - **Potentiometer**: Turn to simulate battery voltage ADC input (pin 34).
6. View serial monitor output printing HTTP JSON telemetry payloads dispatched to `http://floodsense.local/api/readings`.
