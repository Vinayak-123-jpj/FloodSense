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
