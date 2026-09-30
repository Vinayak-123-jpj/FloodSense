"""Virtual Sensor Node Emulator & Simulator Daemon.

Emulates physical ESP32 IoT nodes deployed along rivers. Generates realistic sensor telemetry
including Gaussian measurement noise, battery drain/solar recharge cycles, signal fading (RSSI),
intermittent packet dropouts, and physical sensor faults.
Can run as a background service inside FastAPI or as a standalone CLI script posting to POST /api/readings.
"""

import random
import time
import requests
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Station, Reading, SimulationState

class SensorNodeSimulator:
    """Simulates a cluster of virtual ESP32 sensor nodes."""

    def __init__(self, api_url: str = "http://127.0.0.1:8000/api/readings"):
        self.api_url = api_url
        self.node_states = {}

    def _init_node_state(self, station: Station):
        """Initializes internal physical state for a virtual node."""
        return {
            "water_level_m": station.normal_level_m,
            "rainfall_mm_hr": 0.0,
            "battery_pct": round(random.uniform(85.0, 100.0), 1),
            "rssi": random.randint(-75, -55),
            "trend_direction": 0.0,
            "is_faulty": False
        }

    def simulate_tick(self, use_direct_db: bool = False, db_session: Session = None):
        """Executes a single simulation tick across all monitoring stations."""
        close_db = False
        if use_direct_db and not db_session:
            db_session = SessionLocal()
            close_db = True

        try:
            # Query active simulation settings
            if db_session:
                sim_state = db_session.query(SimulationState).filter(SimulationState.id == 1).first()
                if sim_state and not sim_state.is_running:
                    return
                rain_mult = sim_state.rain_multiplier if sim_state else 1.0
                stations = db_session.query(Station).all()
            else:
                rain_mult = 1.0
                stations = []

            for st in stations:
                if st.id not in self.node_states:
                    self.node_states[st.id] = self._init_node_state(st)

                state = self.node_states[st.id]

                # 1. Weather / Rainfall simulation
                # 5% chance of monsoon rain spell starting
                if random.random() < 0.05:
                    state["rainfall_mm_hr"] = random.uniform(5.0, 45.0) * rain_mult
                else:
                    state["rainfall_mm_hr"] = max(0.0, state["rainfall_mm_hr"] * 0.85)

                # 2. Water level hydrological response to rainfall & discharge decay
                rain_effect = (state["rainfall_mm_hr"] * 0.008)
                discharge_decay = 0.003
                state["water_level_m"] += rain_effect - discharge_decay

                # Ensure water level stays within realistic bounds (never below 0.5m)
                state["water_level_m"] = max(0.5, state["water_level_m"])

                # Add realistic sensor Gaussian measurement noise (+/- 1.5 cm)
                noise_m = random.gauss(0, 0.015)
                measured_water_level_m = max(0.1, state["water_level_m"] + noise_m)
                water_level_cm = measured_water_level_m * 100.0

                # 3. Battery drain & solar panel charge dynamics
                if state["rainfall_mm_hr"] > 0:
                    # Cloud cover -> drain battery
                    state["battery_pct"] = max(5.0, state["battery_pct"] - random.uniform(0.01, 0.05))
                else:
                    # Clear daylight -> solar charging
                    state["battery_pct"] = min(100.0, state["battery_pct"] + random.uniform(0.02, 0.08))

                # 4. RSSI signal fluctuations
                state["rssi"] = max(-110, min(-50, state["rssi"] + random.randint(-3, 3)))

                # 5. Packet loss simulation (2% dropped packet rate)
                if random.random() < 0.02:
                    continue  # Packet dropped!

                # Construct payload identical to physical ESP32 HTTP POST
                payload = {
                    "node_id": st.id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "water_level_cm": round(water_level_cm, 1),
                    "rainfall_mm_hr": round(state["rainfall_mm_hr"], 2),
                    "battery_pct": round(state["battery_pct"], 1),
                    "rssi": state["rssi"],
                    "discharge_m3s": round(state["water_level_m"] * 45.0, 1)
                }

                if use_direct_db:
                    # Direct Python call via API helper
                    from backend.api.readings import calculate_risk_and_drivers, trigger_alert_processing
                    risk_level, top_drivers = calculate_risk_and_drivers(db_session, st, measured_water_level_m, state["rainfall_mm_hr"])
                    
                    db_reading = Reading(
                        station_id=st.id,
                        timestamp=datetime.now(timezone.utc),
                        water_level_cm=round(water_level_cm, 1),
                        water_level_m=round(measured_water_level_m, 2),
                        rainfall_mm_hr=round(state["rainfall_mm_hr"], 2),
                        discharge_m3s=round(state["water_level_m"] * 45.0, 1),
                        battery_pct=round(state["battery_pct"], 1),
                        rssi=state["rssi"],
                        risk_level=risk_level,
                        sensor_status="DEGRADED" if state["battery_pct"] < 15 else "OK",
                        top_drivers=top_drivers
                    )
                    db_session.add(db_reading)
                    db_session.commit()
                    trigger_alert_processing(db_session, st, db_reading)
                else:
                    # HTTP POST to API endpoint
                    try:
                        requests.post(self.api_url, json=payload, timeout=2.0)
                    except Exception:
                        pass
        finally:
            if close_db and db_session:
                db_session.close()

def run_standalone():
    """Runs simulator loop as a standalone CLI application."""
    print("[Simulator] Starting standalone FloodSense virtual sensor node cluster...")
    simulator = SensorNodeSimulator()
    while True:
        try:
            simulator.simulate_tick(use_direct_db=False)
            time.sleep(5)
        except KeyboardInterrupt:
            print("[Simulator] Virtual sensor engine stopped.")
            break
        except Exception as e:
            print(f"[Simulator Error] {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_standalone()
