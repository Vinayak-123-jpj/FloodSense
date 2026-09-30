"""Virtual Sensor Simulator Control API Endpoints.

Provides endpoints to start, pause, adjust playback speed, change historical scenarios,
and inject rain multipliers ('What-If' scenario simulation).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import SimulationState
from backend.schemas import SimulationControl, SimulationStatusResponse

router = APIRouter(prefix="/simulate", tags=["Simulator Control"])

@router.get("/status", response_model=SimulationStatusResponse, summary="Get simulator status")
def get_simulation_status(db: Session = Depends(get_db)):
    """Queries current virtual sensor engine simulation status."""
    state = db.query(SimulationState).filter(SimulationState.id == 1).first()
    if not state:
        state = SimulationState(id=1, is_running=True, speed=1.0, current_scenario="live", rain_multiplier=1.0)
        db.add(state)
        db.commit()
        db.refresh(state)

    return SimulationStatusResponse(
        is_running=state.is_running,
        speed=state.speed,
        current_scenario=state.current_scenario,
        simulated_time=state.simulated_time,
        rain_multiplier=state.rain_multiplier
    )

@router.post("/control", response_model=SimulationStatusResponse, summary="Update simulator parameters")
def control_simulation(payload: SimulationControl, db: Session = Depends(get_db)):
    """Updates simulation state (start/stop/speed/scenario/rain multiplier)."""
    state = db.query(SimulationState).filter(SimulationState.id == 1).first()
    if not state:
        state = SimulationState(id=1)
        db.add(state)

    if payload.action == "start":
        state.is_running = True
    elif payload.action == "stop":
        state.is_running = False
    elif payload.action == "set_speed":
        if payload.speed is not None:
            state.speed = max(0.1, min(100.0, payload.speed))

    if payload.scenario:
        state.current_scenario = payload.scenario
    if payload.rain_multiplier is not None:
        state.rain_multiplier = max(0.0, min(5.0, payload.rain_multiplier))

    db.commit()
    db.refresh(state)

    return SimulationStatusResponse(
        is_running=state.is_running,
        speed=state.speed,
        current_scenario=state.current_scenario,
        simulated_time=state.simulated_time,
        rain_multiplier=state.rain_multiplier
    )

@router.get("/replay", summary="Fetch historical disaster replay frame")
def get_replay_frame(
    scenario: str = "kerala_2018",
    progress_pct: float = 50.0,
    rain_multiplier: float = 1.0
):
    """Fetches real historical day-by-day held-out 2018 replay state with dynamic what-if scaling."""
    import os, json
    
    file_name = f"replay_{scenario}.json" if not scenario.startswith("replay_") else f"{scenario}.json"
    file_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", file_name)
    
    # Fallback to kerala_2018 if not found
    if not os.path.exists(file_path):
        file_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "replay_kerala_2018.json")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Replay dataset not found. Run scripts/generate_replay_dataset.py.")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    frames = data.get("frames", [])
    if not frames:
        raise HTTPException(status_code=404, detail="No replay frames in dataset.")

    # Find closest frame by progress_pct
    target_pct = max(0.0, min(100.0, progress_pct))
    best_frame = min(frames, key=lambda fr: abs(fr["progress_pct"] - target_pct))
    
    # Apply what-if rain multiplier
    mult = max(0.2, min(5.0, rain_multiplier))
    scaled_stations = []
    max_prio = 0
    prio_map = {"Green": 0, "Yellow": 1, "Orange": 2, "Red": 3}
    overall_risk = "Green"

    for st in best_frame["stations"]:
        base_q = st["discharge_m3s"]
        base_rain = st["rainfall_mm"]
        p = st["percentiles"]

        eff_q = round(base_q * (1.0 + (mult - 1.0) * 0.75), 1)
        eff_rain = round(base_rain * mult, 1)

        # Re-evaluate risk
        if eff_q >= p["p99.5_red"]:
            risk = "Red"
        elif eff_q >= p["p97_orange"]:
            risk = "Orange"
        elif eff_q >= p["p90_yellow"]:
            risk = "Yellow"
        else:
            risk = "Green"

        if prio_map.get(risk, 0) > max_prio:
            max_prio = prio_map.get(risk, 0)
            overall_risk = risk

        st_copy = dict(st)
        st_copy["discharge_m3s"] = eff_q
        st_copy["rainfall_mm"] = eff_rain
        st_copy["risk_level"] = risk
        scaled_stations.append(st_copy)

    headline = best_frame["headline"]
    if mult != 1.0:
        headline += f" [What-If: {mult:.1f}x Rain Stress Applied]"

    return {
        "scenario": scenario,
        "date": best_frame["date"],
        "day_index": best_frame["day_index"],
        "progress_pct": best_frame["progress_pct"],
        "headline": headline,
        "overall_risk": overall_risk,
        "rain_multiplier": mult,
        "stations": scaled_stations
    }

