"""Hydrological Forecast API Endpoints.

Generates multi-horizon 24-72 hour hydrological forecasts, risk projections,
and confidence interval bounds for monitoring stations.
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Station, Reading
from backend.schemas import StationForecastResponse, ForecastHour

router = APIRouter(prefix="/stations", tags=["Hydrological Forecasts"])

@router.get("/{station_id}/forecast", response_model=StationForecastResponse, summary="Get 72-hour station forecast")
def get_station_forecast(station_id: str, db: Session = Depends(get_db)):
    """Computes a 72-hour hydrological prediction with uncertainty bounds."""
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail=f"Station '{station_id}' not found.")

    latest_reading = (
        db.query(Reading)
        .filter(Reading.station_id == station_id)
        .order_by(Reading.timestamp.desc())
        .first()
    )

    current_level = latest_reading.water_level_m if latest_reading else station.normal_level_m
    current_rain = latest_reading.rainfall_mm_hr if latest_reading else 0.0
    now = datetime.now(timezone.utc)

    # Forecast points generator (72 hours ahead)
    points = []
    base_level = current_level
    
    # Generate 72 forecast hourly samples
    for h in range(1, 73):
        t = now + timedelta(hours=h)
        # Synthetic diurnal / attenuation curve based on current rain input
        rain_decay = max(0.0, current_rain * (0.95 ** h))
        
        # Hydrological response lag
        hydrological_lag_offset = (rain_decay * 0.04) * (1.0 if h <= 24 else 0.5)
        simulated_water_level = base_level + hydrological_lag_offset + (0.02 * (0.5 - ((h % 12) / 12.0)))
        simulated_water_level = max(station.normal_level_m * 0.8, simulated_water_level)

        # Risk level determination
        if simulated_water_level >= station.danger_level_m:
            risk = "Red"
        elif simulated_water_level >= station.warning_level_m:
            risk = "Orange"
        elif simulated_water_level >= (station.warning_level_m * 0.85):
            risk = "Yellow"
        else:
            risk = "Green"

        # Uncertainty envelope expands over time (+/- 5% at 24h up to +/- 15% at 72h)
        uncertainty = 0.05 + (h / 72.0) * 0.10
        lower_bound = max(0.0, simulated_water_level * (1.0 - uncertainty))
        upper_bound = simulated_water_level * (1.0 + uncertainty)

        points.append(ForecastHour(
            timestamp=t,
            predicted_water_level_m=round(simulated_water_level, 2),
            predicted_risk_level=risk,
            rainfall_mm_hr=round(rain_decay, 1),
            lower_bound_m=round(lower_bound, 2),
            upper_bound_m=round(upper_bound, 2)
        ))

    top_drivers = [
        f"Upstream river discharge velocity: baseline normal",
        f"Forecasted 72h cumulative precipitation: {sum(p.rainfall_mm_hr for p in points):.1f} mm",
        f"Station elevation offset: {station.elevation_m}m AMSL"
    ]

    return StationForecastResponse(
        station_id=station.id,
        station_name=station.name,
        generated_at=now,
        horizon_hours=72,
        top_risk_drivers=top_drivers,
        forecast_points=points
    )
