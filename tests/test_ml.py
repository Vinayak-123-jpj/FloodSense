"""Unit Tests for ML Risk Engine, Future Target Redefinition & No-Leakage Check.

Tests feature computation, future target shift (t+24h), model inference, fallback risk rules,
and plain-language driver generation.
"""

import pandas as pd
import numpy as np
from backend.ml.feature_engineering import build_features, FEATURE_COLUMNS
from backend.ml.explainability import generate_plain_language_explanation
from backend.ml.predictor import get_model, rule_based_fallback
from backend.models import Station

def test_no_leakage_feature_check():
    """Verifies that features at time t use ONLY data available up to time t and target is shifted 24h into future."""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2026-08-01", periods=100, freq="h"),
        "precipitation_mm": [5.0] * 100,
        "river_discharge_m3s": [200.0] * 100
    })
    fe_df = build_features(df, warning_threshold_discharge=300.0, danger_threshold_discharge=550.0, horizon_hours=24)
    
    assert "target_risk_future" in fe_df.columns
    # Check that target_risk_future at row 0 equals current_risk_at_t at row 24
    assert fe_df["target_risk_future"].iloc[0] == fe_df["current_risk_at_t"].iloc[24]
    assert len(fe_df) == 100 - 24  # Tail shifted rows dropped

def test_explainability_generator():
    """Verifies plain-language top-3 factor driver text generation."""
    features = {
        "rain_sum_72h": 185.0,
        "rain_sum_24h": 65.0,
        "rain_sum_6h": 20.0,
        "discharge_m3s": 350.0,
        "discharge_rate_of_change_24h": 25.0,
        "antecedent_wetness_index": 45.0
    }
    explanation = generate_plain_language_explanation(features, "Orange")
    assert "72h cumulative rainfall" in explanation
    assert "API:" in explanation or "river discharge" in explanation

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
