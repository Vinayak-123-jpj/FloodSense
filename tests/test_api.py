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

def test_telemetry_reading_schema_contract():
    """Validates that telemetry payload contract satisfies docs/api/reading.schema.json."""
    import json, os, re
    schema_path = os.path.join(os.path.dirname(__file__), "..", "docs", "api", "reading.schema.json")
    assert os.path.exists(schema_path), "Schema file missing"
    
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    sample_payload = {
        "node_id": "KL-PER-01",
        "water_level_cm": 450.0,
        "rainfall_mm_hr": 12.5,
        "battery_pct": 99.0,
        "rssi": -65
    }

    # Validate required fields
    for req_field in schema.get("required", []):
        assert req_field in sample_payload, f"Missing required field: {req_field}"

    # Validate patterns & ranges
    node_id_pattern = schema["properties"]["node_id"]["pattern"]
    assert re.match(node_id_pattern, sample_payload["node_id"])
    assert schema["properties"]["water_level_cm"]["minimum"] <= sample_payload["water_level_cm"] <= schema["properties"]["water_level_cm"]["maximum"]
    assert schema["properties"]["rainfall_mm_hr"]["minimum"] <= sample_payload["rainfall_mm_hr"] <= schema["properties"]["rainfall_mm_hr"]["maximum"]
    assert schema["properties"]["battery_pct"]["minimum"] <= sample_payload["battery_pct"] <= schema["properties"]["battery_pct"]["maximum"]
    assert schema["properties"]["rssi"]["minimum"] <= sample_payload["rssi"] <= schema["properties"]["rssi"]["maximum"]



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

def test_get_real_live_station_data_success(monkeypatch):
    """Verifies GET /api/stations/{id}/real_live returns Open-Meteo response structure."""
    mock_flood = {
        "daily": {
            "time": ["2026-09-25", "2026-09-26", "2026-09-27", "2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01"],
            "river_discharge": [100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0]
        }
    }
    mock_weather = {
        "daily": {
            "time": ["2026-09-25", "2026-09-26", "2026-09-27", "2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01"],
            "precipitation_sum": [10.0, 15.0, 20.0, 5.0, 0.0, 12.0, 8.0]
        }
    }
    
    class MockResponse:
        def __init__(self, json_data, status_code):
            self._json_data = json_data
            self.status_code = status_code
        def json(self):
            return self._json_data

    def mock_get(url, timeout=3.5):
        if "flood" in url:
            return MockResponse(mock_flood, 200)
        return MockResponse(mock_weather, 200)

    import requests
    monkeypatch.setattr(requests, "get", mock_get)

    with TestClient(app) as client:
        response = client.get("/api/stations/KL-PER-01/real_live")
        assert response.status_code == 200
        data = response.json()
        assert data["station_id"] == "KL-PER-01"
        assert "forecast_horizons" in data
        assert "1d_risk" in data["forecast_horizons"]
        assert "data_source" in data

def test_get_real_live_station_data_failure_fallback(monkeypatch):
    """Verifies GET /api/stations/{id}/real_live falls back to cache/mock on network failure."""
    import requests
    def mock_failing_get(url, timeout=3.5):
        raise requests.RequestException("Network timeout")

    monkeypatch.setattr(requests, "get", mock_failing_get)

    with TestClient(app) as client:
        response = client.get("/api/stations/KL-PER-01/real_live")
        assert response.status_code == 200
        data = response.json()
        assert data["station_id"] == "KL-PER-01"
        assert data.get("is_cached") is True or "fetched_at" in data


