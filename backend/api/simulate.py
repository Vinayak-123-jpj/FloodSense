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
