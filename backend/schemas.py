"""Pydantic Request & Response Data Validation Schemas.

Enforces structural schema contracts for REST API endpoints, telemetry payloads,
forecast data objects, and alert outbox responses.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class ReadingCreate(BaseModel):
    """Payload received from physical ESP32 node or virtual sensor simulator."""
    node_id: str = Field(..., description="Unique station hardware node identifier (e.g. KL-PER-01)")
    timestamp: Optional[datetime] = Field(None, description="ISO timestamp of measurement")
    water_level_cm: float = Field(..., description="Raw water level height measured in cm")
    rainfall_mm_hr: float = Field(0.0, description="Precipitation rate in mm/hour")
    battery_pct: float = Field(100.0, description="Node battery percentage (0-100%)")
    rssi: int = Field(-65, description="Cellular or Wi-Fi signal strength in dBm")
    discharge_m3s: Optional[float] = Field(0.0, description="Estimated or river discharge rate in m³/s")

class ReadingResponse(BaseModel):
    """Public reading model returned by telemetry endpoints."""
    id: int
    station_id: str
    timestamp: datetime
    water_level_cm: float
    water_level_m: float
    rainfall_mm_hr: float
    discharge_m3s: Optional[float]
    battery_pct: float
    rssi: int
    risk_level: str
    sensor_status: str
    top_drivers: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class StationResponse(BaseModel):
    """Monitoring station detail schema."""
    id: str
    name: str
    region: str
    river: str
    latitude: float
    longitude: float
    elevation_m: float
    warning_level_m: float
    danger_level_m: float
    normal_level_m: float
    p90_m3s: Optional[float] = None
    p97_m3s: Optional[float] = None
    p99_5_m3s: Optional[float] = None
    historical_max_m3s: Optional[float] = None
    current_discharge_m3s: Optional[float] = None
    data_source_label: Optional[str] = None
    description: Optional[str]
    current_water_level_m: Optional[float] = None
    current_risk_level: Optional[str] = "Green"
    battery_pct: Optional[float] = 100.0
    rssi: Optional[int] = -65
    sensor_status: Optional[str] = "OK"

    model_config = ConfigDict(from_attributes=True)

class ForecastHour(BaseModel):
    """Single hour hydrological forecast point."""
    timestamp: datetime
    predicted_water_level_m: float
    predicted_risk_level: str
    rainfall_mm_hr: float
    lower_bound_m: float
    upper_bound_m: float

class StationForecastResponse(BaseModel):
    """72-hour forecast response container."""
    station_id: str
    station_name: str
    generated_at: datetime
    horizon_hours: int = 72
    top_risk_drivers: List[str]
    forecast_points: List[ForecastHour]

class AlertResponse(BaseModel):
    """Alert outbox and history item response schema."""
    id: int
    station_id: str
    station_name: Optional[str] = None
    timestamp: datetime
    risk_level: str
    previous_risk_level: str
    reason: str
    action_recommended: str
    evacuation_route_url: Optional[str]
    language: str
    sent_to_telegram: bool
    outbox_logged: bool

    model_config = ConfigDict(from_attributes=True)

class SimulationControl(BaseModel):
    """Payload to update virtual simulator execution parameters."""
    action: str = Field(..., description="'start', 'stop', or 'set_speed'")
    speed: Optional[float] = Field(1.0, description="Simulation time acceleration factor (0.5x to 60x)")
    scenario: Optional[str] = Field("live", description="'live', 'kerala_2018', or 'assam_2020'")
    rain_multiplier: Optional[float] = Field(1.0, description="What-if rain multiplier (1.0 to 3.0)")

class SimulationStatusResponse(BaseModel):
    """Current simulator status model."""
    is_running: bool
    speed: float
    current_scenario: str
    simulated_time: datetime
    rain_multiplier: float
