"""ML Risk Inference & Rule-Based Fallback Predictor.

Loads serialized LightGBM risk classifier to execute real-time model inference.
Includes physical threshold safety overrides and rule-based fallback when model binaries are absent.
"""

import os
import joblib
import pandas as pd
import numpy as np
from typing import Tuple, Dict
from sqlalchemy.orm import Session

from backend.models import Station, Reading
from backend.ml.feature_engineering import FEATURE_COLUMNS
from backend.ml.explainability import generate_plain_language_explanation

RISK_MAP = {0: "Green", 1: "Yellow", 2: "Orange", 3: "Red"}
_MODEL_CACHE = None

def get_model():
    """Returns cached LightGBM model or attempts loading from disk."""
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE
    
    model_path = os.path.join(os.path.dirname(__file__), "..", "..", "models", "flood_risk_model.joblib")
    if os.path.exists(model_path):
        try:
            _MODEL_CACHE = joblib.load(model_path)
            print("[Predictor] Successfully loaded serialized LightGBM risk model.")
            return _MODEL_CACHE
        except Exception as e:
            print(f"[Predictor Warning] Failed loading model artifact: {e}")
    return None

def compute_historical_features(db: Session, station: Station, current_water_level_m: float, current_rain_mm_hr: float) -> Dict[str, float]:
    """Retrieves recent 72h historical readings from DB to compute rolling feature inputs."""
    recent_readings = (
        db.query(Reading)
        .filter(Reading.station_id == station.id)
        .order_by(Reading.timestamp.desc())
        .limit(72)
        .all()
    )
    
    past_rains = [r.rainfall_mm_hr for r in reversed(recent_readings)] if recent_readings else []
    past_rains.append(current_rain_mm_hr)

    r6 = sum(past_rains[-6:]) if past_rains else current_rain_mm_hr
    r24 = sum(past_rains[-24:]) if past_rains else current_rain_mm_hr
    r72 = sum(past_rains[-72:]) if past_rains else current_rain_mm_hr

    discharge = current_water_level_m * 45.0
    
    past_discharges = [r.discharge_m3s for r in reversed(recent_readings)] if recent_readings else []
    d24_old = past_discharges[0] if len(past_discharges) >= 24 else discharge
    d_roc = discharge - d24_old

    api = 0.0
    for rain in past_rains:
        api = api * 0.85 + rain

    return {
        "rain_sum_6h": r6,
        "rain_sum_24h": r24,
        "rain_sum_72h": r72,
        "discharge_m3s": discharge,
        "discharge_rate_of_change_24h": d_roc,
        "antecedent_wetness_index": api,
        "month": 8,
        "day_of_year": 230
    }

def rule_based_fallback(station: Station, water_level_m: float, rain_72h: float) -> str:
    """Fallback rule engine when ML model is absent."""
    if water_level_m >= station.danger_level_m or rain_72h >= 250.0:
        return "Red"
    elif water_level_m >= station.warning_level_m or rain_72h >= 150.0:
        return "Orange"
    elif water_level_m >= (station.warning_level_m * 0.85) or rain_72h >= 75.0:
        return "Yellow"
    return "Green"

def predict_risk_for_reading(db: Session, station: Station, water_level_m: float, rainfall_mm_hr: float) -> Tuple[str, str]:
    """Main predictor entrypoint returning (risk_level, plain_language_drivers)."""
    features = compute_historical_features(db, station, water_level_m, rainfall_mm_hr)
    model = get_model()

    if model is not None:
        try:
            input_df = pd.DataFrame([features])[FEATURE_COLUMNS]
            pred_class = int(model.predict(input_df)[0])
            risk_level = RISK_MAP.get(pred_class, "Green")
        except Exception as e:
            print(f"[Predictor Warning] Inference error ({e}), falling back to rules.")
            risk_level = rule_based_fallback(station, water_level_m, features["rain_sum_72h"])
    else:
        risk_level = rule_based_fallback(station, water_level_m, features["rain_sum_72h"])

    # Physical safety override: Water level exceeding station physical danger level MUST be Red
    if water_level_m >= station.danger_level_m:
        risk_level = "Red"
    elif water_level_m >= station.warning_level_m and risk_level in ["Green", "Yellow"]:
        risk_level = "Orange"

    drivers_text = generate_plain_language_explanation(features, risk_level)
    return risk_level, drivers_text
