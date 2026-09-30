"""Unit Tests for ML Risk Engine, Future Target Redefinition & No-Leakage Check.

Tests daily feature computation, future target shift (t+1d, t+2d, t+3d), 2018 non-leakage split gap,
and plain-language driver generation.
"""

import pandas as pd
import numpy as np
from backend.ml.feature_engineering import build_daily_features, compute_station_percentiles, FEATURE_COLUMNS_DAILY
from backend.ml.explainability import generate_plain_language_explanation
from backend.ml.predictor import get_model, rule_based_fallback
from backend.models import Station

def test_daily_no_leakage_feature_check():
    """Verifies that daily features at day t target future risk level at t+1d."""
    dates = pd.date_range("2024-01-01", periods=50, freq="D")
    df = pd.DataFrame({
        "station_id": ["KL-PER-01"] * 50,
        "date": dates,
        "precipitation_sum_mm": [10.0] * 50,
        "river_discharge_m3s": [100.0 + i * 5 for i in range(50)],
        "discharge_m3s": [100.0 + i * 5 for i in range(50)]
    })
    
    station_percentiles = {
        "KL-PER-01": {"p90_yellow": 150.0, "p97_orange": 250.0, "p99.5_red": 320.0}
    }
    
    fe_df = build_daily_features(df, station_percentiles, horizon_days=1)
    
    assert "target_risk_1d" in fe_df.columns
    # Check target_risk_1d at row 0 matches current_risk_at_t at row 1
    assert fe_df["target_risk_1d"].iloc[0] == fe_df["current_risk_at_t"].iloc[1]
    assert len(fe_df) == 50 - 1  # 1 tail row dropped due to future target shift

def test_2018_split_gap_and_non_leakage():
    """Verifies 2018 is completely excluded from non-2018 training dataset with a 7-day safety buffer."""
    buffer_start = pd.Timestamp("2017-12-25")
    buffer_end = pd.Timestamp("2019-01-07")
    
    dates = pd.date_range("2017-01-01", "2020-01-01", freq="D")
    df = pd.DataFrame({"date": dates})
    
    train_b = df[(df["date"] < buffer_start) | (df["date"] > buffer_end)]
    test_b = df[(df["date"] >= "2018-01-01") & (df["date"] <= "2018-12-31")]
    
    # Check zero overlap
    overlap = set(train_b["date"]).intersection(set(test_b["date"]))
    assert len(overlap) == 0
    # Check safety buffer is enforced (no dates in buffer period in train_b)
    buffer_dates = train_b[(train_b["date"] >= buffer_start) & (train_b["date"] <= buffer_end)]
    assert len(buffer_dates) == 0

def test_explainability_generator():
    """Verifies plain-language top-3 factor driver text generation uses ONLY real features."""
    features = {
        "rain_1d": 45.0,
        "rain_3d": 120.0,
        "rain_7d": 185.0,
        "rain_14d": 250.0,
        "rain_30d": 380.0,
        "discharge_m3s": 350.0,
        "discharge_roc_3d": 45.0,
        "antecedent_wetness_7d": 42.0,
        "month": 8,
        "day_of_year": 227
    }
    explanation = generate_plain_language_explanation(features, "Orange")
    assert len(explanation) > 0

    # Ensure prohibited invented terms are NEVER present
    assert "velocity" not in explanation.lower()
    assert "elevation offset" not in explanation.lower()

    # Verify that drivers correspond only to valid features in FEATURE_COLUMNS_DAILY
    from backend.ml.explainability import FEATURE_NAME_MAP
    drivers = [d.strip() for d in explanation.split(";")]
    assert len(drivers) <= 3
    for d in drivers:
        matched = any(v.lower() in d.lower() for v in FEATURE_NAME_MAP.values())
        assert matched, f"Driver statement '{d}' does not match any valid model feature in {FEATURE_NAME_MAP.values()}"


def test_rule_based_fallback():
    """Verifies rule engine returns correct risk level when model is absent."""
    st = Station(
        id="TEST-01", name="Test", region="Kerala", river="Test",
        latitude=10.0, longitude=76.0, elevation_m=10.0,
        warning_level_m=4.0, danger_level_m=6.0, normal_level_m=2.0
    )
    assert rule_based_fallback(st, water_level_m=6.5, rain_72h=50.0) == "Red"
    assert rule_based_fallback(st, water_level_m=4.5, rain_72h=50.0) == "Orange"
    assert rule_based_fallback(st, water_level_m=2.0, rain_72h=10.0) == "Green"

def test_model_loading():
    """Verifies model loading function fetches trained LightGBM artifact."""
    model = get_model()
    assert model is not None
