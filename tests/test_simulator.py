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

def test_replay_kerala_2018_data_integrity_and_diversity():
    """Verifies that at 1.0x multiplier, replay discharge on peak-discharge days matches CSV,
    and station risk classes are not identical across all six Kerala stations on at least 50% of days in August 2018.
    """
    import os
    import pandas as pd
    from fastapi.testclient import TestClient
    from backend.main import app

    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "kerala_daily_1990_2025.csv")
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"].astype(str).str[:10])
    aug = df[(df["date"] >= "2018-08-01") & (df["date"] <= "2018-08-31")]

    # Find peak discharge date & value for each station
    peaks = {}
    for st_id, g in aug.groupby("station_id"):
        max_row = g.loc[g["river_discharge_m3s"].idxmax()]
        peaks[st_id] = {
            "date": str(max_row["date"])[:10],
            "discharge": float(max_row["river_discharge_m3s"])
        }

    with TestClient(app) as client:
        # 1. Verify peak discharge day values match CSV exactly at 1.0x
        for st_id, peak_info in peaks.items():
            dt_str = peak_info["date"]
            day_idx = int(dt_str.split("-")[2]) - 1 # 0-indexed day
            pct = round((day_idx / 30.0) * 100.0, 1)

            res = client.get(f"/api/simulate/replay?scenario=kerala_2018&progress_pct={pct}&rain_multiplier=1.0")
            assert res.status_code == 200
            data = res.json()
            st_data = next((s for s in data["stations"] if s["id"] == st_id), None)
            assert st_data is not None, f"Station {st_id} missing in replay"
            assert abs(st_data["discharge_m3s"] - round(peak_info["discharge"], 1)) < 0.1, \
                f"Peak discharge mismatch for {st_id}: expected {peak_info['discharge']}, got {st_data['discharge_m3s']}"

        # 2. Check risk class diversity across August 2018 (>= 50% not-identical days)
        not_identical_count = 0
        total_days = 31

        for day in range(1, 32):
            pct = round(((day - 1) / 30.0) * 100.0, 1)
            res = client.get(f"/api/simulate/replay?scenario=kerala_2018&progress_pct={pct}&rain_multiplier=1.0")
            assert res.status_code == 200
            data = res.json()

            risks = [s["risk_level"] for s in data["stations"]]
            if len(set(risks)) > 1:
                not_identical_count += 1

        diversity_ratio = not_identical_count / total_days
        assert diversity_ratio >= 0.50, f"Risk classes were identical on too many days: {not_identical_count}/31 = {diversity_ratio:.2%}"


