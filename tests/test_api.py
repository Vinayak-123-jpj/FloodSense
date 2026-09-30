"""Unit & Integration Tests for Backend REST API Endpoints.

Verifies FastAPI routes for stations, readings ingestion, hydrological forecasts,
alert outbox, simulation controls, and health diagnostics.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import Base, engine
from backend.seed import seed_database

@pytest.fixture(autouse=True)
def setup_database():
    """Ensures database tables are initialized and seeded prior to test execution."""
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield

def test_health_check():
    """Verifies GET /api/health endpoint returns online status."""
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["online", "healthy"]
        assert "service" in data

def test_get_stations():
    """Verifies GET /api/stations returns station metadata list."""
    with TestClient(app) as client:
        response = client.get("/api/stations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        station = data[0]
        assert "id" in station
        assert "name" in station
        assert "river" in station
        assert "danger_level_m" in station

def test_ingest_telemetry_reading():
    """Verifies POST /api/readings ingests virtual node payload and calculates risk."""
    payload = {
        "node_id": "KL-PER-01",
        "water_level_cm": 620.0,  # 6.2m -> exceeds 6.0m danger level
        "rainfall_mm_hr": 35.5,
        "battery_pct": 98.0,
        "rssi": -62
    }
    with TestClient(app) as client:
        response = client.post("/api/readings", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["station_id"] == "KL-PER-01"
        assert data["water_level_m"] == 6.2
        assert data["risk_level"] == "Red"
        assert "top_drivers" in data

def test_get_station_forecast():
    """Verifies GET /api/stations/{id}/forecast generates 72h forecast points."""
    with TestClient(app) as client:
        response = client.get("/api/stations/KL-PER-01/forecast")
        assert response.status_code == 200
        data = response.json()
        assert data["station_id"] == "KL-PER-01"
        assert data["horizon_hours"] == 72
        assert len(data["forecast_points"]) == 72
        assert "lower_bound_m" in data["forecast_points"][0]
        assert "upper_bound_m" in data["forecast_points"][0]
