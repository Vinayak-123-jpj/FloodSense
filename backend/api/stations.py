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
        # Fetch latest reading to attach live status
        latest_reading = (
            db.query(Reading)
            .filter(Reading.station_id == st.id)
            .order_by(Reading.timestamp.desc())
            .first()
        )
        
        st_dict = {
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
            "description": st.description,
            "current_water_level_m": latest_reading.water_level_m if latest_reading else st.normal_level_m,
            "current_risk_level": latest_reading.risk_level if latest_reading else "Green",
            "battery_pct": latest_reading.battery_pct if latest_reading else 100.0,
            "rssi": latest_reading.rssi if latest_reading else -65,
            "sensor_status": latest_reading.sensor_status if latest_reading else "OK"
        }
        result.append(StationResponse(**st_dict))
    
    return result

@router.get("/{station_id}", response_model=StationResponse, summary="Get station details by ID")
def get_station_by_id(station_id: str, db: Session = Depends(get_db)):
    """Retrieves full details and live status for a specific station."""
    st = db.query(Station).filter(Station.id == station_id).first()
    if not st:
        raise HTTPException(status_code=404, detail=f"Station with ID '{station_id}' not found.")
    
    latest_reading = (
        db.query(Reading)
        .filter(Reading.station_id == st.id)
        .order_by(Reading.timestamp.desc())
        .first()
    )

    st_dict = {
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
        "description": st.description,
        "current_water_level_m": latest_reading.water_level_m if latest_reading else st.normal_level_m,
        "current_risk_level": latest_reading.risk_level if latest_reading else "Green",
        "battery_pct": latest_reading.battery_pct if latest_reading else 100.0,
        "rssi": latest_reading.rssi if latest_reading else -65,
        "sensor_status": latest_reading.sensor_status if latest_reading else "OK"
    }
    return StationResponse(**st_dict)

@router.get("/{station_id}/real_live", summary="Fetch real Open-Meteo live observed data & GloFAS forecast")
def get_real_live_station_data(station_id: str, db: Session = Depends(get_db)):
    """Fetches real live observed rainfall and GloFAS discharge reanalysis from Open-Meteo with caching fallback."""
    st = db.query(Station).filter(Station.id == station_id).first()
    if not st:
        raise HTTPException(status_code=404, detail=f"Station with ID '{station_id}' not found.")
    
    from backend.services.real_data_service import fetch_real_live_station_data
    return fetch_real_live_station_data(st)
