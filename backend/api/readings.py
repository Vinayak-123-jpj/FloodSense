"""Sensor Telemetry Reading Ingestion & Historical Query Endpoints.

Handles incoming HTTP POST telemetry payloads from physical or virtual sensors,
triggers risk classification, logs readings, and broadcasts updates over WebSocket.
"""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Station, Reading
from backend.schemas import ReadingCreate, ReadingResponse
from backend.api.websocket import manager as ws_manager

router = APIRouter(tags=["Telemetry Readings"])

def calculate_risk_and_drivers(db: Session, station: Station, water_level_m: float, rainfall_mm_hr: float):
    """Calculates risk level and plain-language driver text for a reading."""
    # Attempt importing ML predictor module (built in Phase 2)
    try:
        from backend.ml.predictor import predict_risk_for_reading
        return predict_risk_for_reading(db, station, water_level_m, rainfall_mm_hr)
    except ImportError:
        pass
    
    # Rule-based fallback risk classification logic
    top_drivers = []
    if water_level_m >= station.danger_level_m:
        risk = "Red"
        top_drivers.append(f"Water level ({water_level_m:.2f}m) exceeds danger threshold ({station.danger_level_m:.2f}m)")
    elif water_level_m >= station.warning_level_m:
        risk = "Orange"
        top_drivers.append(f"Water level ({water_level_m:.2f}m) exceeds warning threshold ({station.warning_level_m:.2f}m)")
    elif water_level_m >= (station.warning_level_m * 0.85):
        risk = "Yellow"
        top_drivers.append(f"Water level ({water_level_m:.2f}m) approaching warning threshold")
    else:
        risk = "Green"
        top_drivers.append("Hydrological parameters within seasonal baseline limits")

    if rainfall_mm_hr > 30.0:
        top_drivers.append(f"Heavy rainfall detected ({rainfall_mm_hr:.1f} mm/hr)")
    elif rainfall_mm_hr > 10.0:
        top_drivers.append(f"Moderate rainfall ({rainfall_mm_hr:.1f} mm/hr)")

    driver_str = "; ".join(top_drivers)
    return risk, driver_str

def trigger_alert_processing(db: Session, station: Station, new_reading: Reading):
    """Checks for risk state transitions and fires alert engine if needed."""
    try:
        from backend.alerts.alert_engine import process_reading_for_alert
        process_reading_for_alert(db, station, new_reading)
    except ImportError:
        pass

@router.post("/readings", response_model=ReadingResponse, summary="Ingest node sensor reading payload")
async def create_reading(
    payload: ReadingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Primary telemetry ingest endpoint used by virtual simulator and physical ESP32 nodes."""
    station = db.query(Station).filter(Station.id == payload.node_id).first()
    if not station:
        raise HTTPException(status_code=404, detail=f"Station '{payload.node_id}' not found in database.")

    water_level_m = payload.water_level_cm / 100.0
    timestamp = payload.timestamp or datetime.now(timezone.utc)

    # Sensor health classification
    sensor_status = "OK"
    if payload.battery_pct < 15.0 or payload.rssi < -95:
        sensor_status = "DEGRADED"
    if payload.water_level_cm < 0.0 or payload.water_level_cm > 2000.0:
        sensor_status = "FAULT"

    # Risk evaluation & driver explanation
    risk_level, top_drivers = calculate_risk_and_drivers(db, station, water_level_m, payload.rainfall_mm_hr)

    db_reading = Reading(
        station_id=station.id,
        timestamp=timestamp,
        water_level_cm=payload.water_level_cm,
        water_level_m=water_level_m,
        rainfall_mm_hr=payload.rainfall_mm_hr,
        discharge_m3s=payload.discharge_m3s or 0.0,
        battery_pct=payload.battery_pct,
        rssi=payload.rssi,
        risk_level=risk_level,
        sensor_status=sensor_status,
        top_drivers=top_drivers
    )

    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)

    # Check alert rules
    trigger_alert_processing(db, station, db_reading)

    # Broadcast update over WebSocket
    ws_payload = {
        "type": "new_reading",
        "station_id": station.id,
        "station_name": station.name,
        "water_level_m": water_level_m,
        "rainfall_mm_hr": payload.rainfall_mm_hr,
        "risk_level": risk_level,
        "sensor_status": sensor_status,
        "battery_pct": payload.battery_pct,
        "timestamp": timestamp.isoformat()
    }
    background_tasks.add_task(ws_manager.broadcast, ws_payload)

    return db_reading

@router.get("/stations/{station_id}/readings", response_model=List[ReadingResponse], summary="Get historical readings for station")
def get_station_readings(
    station_id: str,
    limit: int = Query(100, ge=1, le=2000),
    db: Session = Depends(get_db)
):
    """Returns historical time-series sensor telemetry for a given station."""
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail=f"Station '{station_id}' not found.")

    readings = (
        db.query(Reading)
        .filter(Reading.station_id == station_id)
        .order_by(Reading.timestamp.desc())
        .limit(limit)
        .all()
    )
    # Return chronologically ordered list for chart rendering
    return list(reversed(readings))
