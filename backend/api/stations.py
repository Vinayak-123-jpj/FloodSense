"""Station Management & Telemetry Query API Endpoints.

Exposes REST endpoints to query monitoring station metadata, location coordinates,
warning thresholds, and current operational metrics.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Station, Reading
from backend.schemas import StationResponse

router = APIRouter(prefix="/stations", tags=["Stations"])

import os
import json

THRESHOLDS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "thresholds.json")
try:
    with open(THRESHOLDS_PATH, "r", encoding="utf-8") as f:
        THRESHOLDS = json.load(f)
except Exception:
    THRESHOLDS = {}

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cache")

def _get_station_dict(st: Station, db: Session) -> dict:
    latest_reading = (
        db.query(Reading)
        .filter(Reading.station_id == st.id)
        .order_by(Reading.timestamp.desc())
        .first()
    )
    p_params = THRESHOLDS.get(st.id, {"p90_yellow": 160.0, "p97_orange": 310.0, "p99.5_red": 550.0})
    
    current_q = latest_reading.discharge_m3s if (latest_reading and latest_reading.discharge_m3s is not None) else None
    source_label = "REAL (Open-Meteo)"
    
    # Check cached snapshot if DB has no reading
    if current_q is None:
        cache_path = os.path.join(CACHE_DIR, f"{st.id}_live.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    cdata = json.load(f)
                    current_q = cdata.get("current_observed_discharge_m3s")
                    fetched_dt = cdata.get("fetched_at", "")[:10]
                    source_label = f"CACHED {fetched_dt}" if fetched_dt else "CACHED"
            except Exception:
                pass

    return {
        "id": st.id,
        "name": st.name,
        "region": st.region,
        "river": st.river,
        "latitude": st.latitude,
        "longitude": st.longitude,
        "elevation_m": st.elevation_m,
        "warning_level_m": st.warning_level_m,
        "danger_level_m": st.danger_level_m,
        "normal_level_m": st.normal_level_m,
        "p90_m3s": p_params.get("p90_yellow"),
        "p97_m3s": p_params.get("p97_orange"),
        "p99_5_m3s": p_params.get("p99.5_red"),
        "current_discharge_m3s": current_q,
        "data_source_label": source_label,
        "description": st.description,
        "current_water_level_m": latest_reading.water_level_m if latest_reading else st.normal_level_m,
        "current_risk_level": latest_reading.risk_level if latest_reading else "Green",
        "battery_pct": latest_reading.battery_pct if latest_reading else 100.0,
        "rssi": latest_reading.rssi if latest_reading else -65,
        "sensor_status": latest_reading.sensor_status if latest_reading else "OK"
    }

@router.get("", response_model=List[StationResponse], summary="List all river monitoring stations")
def get_stations(
    region: str = Query(None, description="Optional region filter (e.g. 'Kerala' or 'Assam')"),
    db: Session = Depends(get_db)
):
    """Retrieves all registered monitoring stations with their latest readings and risk status."""
    query = db.query(Station)
    if region:
        query = query.filter(Station.region == region)
    stations = query.all()

    result = []
    for st in stations:
        st_dict = _get_station_dict(st, db)
        result.append(StationResponse(**st_dict))
    
    return result

@router.get("/{station_id}", response_model=StationResponse, summary="Get station details by ID")
def get_station_by_id(station_id: str, db: Session = Depends(get_db)):
    """Retrieves full details and live status for a specific station."""
    st = db.query(Station).filter(Station.id == station_id).first()
    if not st:
        raise HTTPException(status_code=404, detail=f"Station with ID '{station_id}' not found.")
    
    st_dict = _get_station_dict(st, db)
    return StationResponse(**st_dict)

@router.get("/{station_id}/real_live", summary="Fetch real Open-Meteo live observed data & GloFAS forecast")
def get_real_live_station_data(station_id: str, db: Session = Depends(get_db)):
    """Fetches real live observed rainfall and GloFAS discharge reanalysis from Open-Meteo with caching fallback."""
    st = db.query(Station).filter(Station.id == station_id).first()
    if not st:
        raise HTTPException(status_code=404, detail=f"Station with ID '{station_id}' not found.")
    
    from backend.services.real_data_service import fetch_real_live_station_data
    return fetch_real_live_station_data(st)
