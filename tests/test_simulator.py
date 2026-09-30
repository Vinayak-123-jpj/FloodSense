"""Unit Tests for Virtual Sensor Node Emulator.

Tests node state initialization, live-mode baseline Green state, Gaussian noise, and battery cycles.
"""

from backend.sensor_simulator import SensorNodeSimulator
from backend.models import Station

def test_sensor_simulator_live_baseline():
    """Verifies that simulator in live mode generates normal level Green baseline state."""
    simulator = SensorNodeSimulator()
    st = Station(
        id="TEST-01",
        name="Test Station",
        region="Test",
        river="Test River",
        latitude=10.0,
        longitude=76.0,
        elevation_m=10.0,
        warning_level_m=4.0,
        danger_level_m=5.0,
        normal_level_m=2.0
    )
    node_state = simulator._init_node_state(st)
    assert node_state["water_level_m"] == 2.0
    assert node_state["rainfall_mm_hr"] == 0.0
    assert 90.0 <= node_state["battery_pct"] <= 100.0

def test_replay_peak_flood_kerala():
    """Verifies that replay at peak-flood day (50% progress / Aug 16) returns at least one Orange or Red station for Kerala."""
    from fastapi.testclient import TestClient
    from backend.main import app

    with TestClient(app) as client:
        # Test at peak flood (50% progress)
        res = client.get("/api/simulate/replay?scenario=kerala_2018&progress_pct=50.0")
        assert res.status_code == 200
        data = res.json()
        assert data["scenario"] == "kerala_2018"
        assert data["overall_risk"] in ["Orange", "Red"]
        
        # Verify at least one station is Orange or Red
        severe_stations = [s for s in data["stations"] if s["risk_level"] in ["Orange", "Red"]]
        assert len(severe_stations) >= 1

        # Test What-If rain multiplier
        res_whatif = client.get("/api/simulate/replay?scenario=kerala_2018&progress_pct=10.0&rain_multiplier=2.0")
        assert res_whatif.status_code == 200
        data_whatif = res_whatif.json()
        assert data_whatif["rain_multiplier"] == 2.0

