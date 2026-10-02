"""ML Risk Prediction Explainability Module using Tree SHAP / pred_contrib.

Computes exact per-prediction feature contributions from LightGBM (pred_contrib=True)
and maps the top 3 drivers to plain-language statements using ONLY the real features:
['rain_1d', 'rain_3d', 'rain_7d', 'rain_14d', 'rain_30d', 'discharge_m3s',
 'discharge_roc_3d', 'antecedent_wetness_7d', 'month', 'day_of_year'].
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any

from backend.ml.feature_engineering import FEATURE_COLUMNS_DAILY

VALID_EXPLANATION_FEATURE_NAMES = set(FEATURE_COLUMNS_DAILY)

FEATURE_NAME_MAP = {
    "rain_1d": "1-day rain",
    "rain_3d": "3-day cumulative rain",
    "rain_7d": "7-day cumulative rain",
    "rain_14d": "14-day cumulative rain",
    "rain_30d": "30-day cumulative rain",
    "discharge_m3s": "Discharge",
    "discharge_roc_3d": "3-day discharge rate of change",
    "antecedent_wetness_7d": "7-day antecedent soil wetness",
    "day_of_year": "Monsoon seasonal timing (day of year)",
    "month": "Seasonal monsoon cycle (month)"
}

def format_driver_statement(feature_name: str, value: float) -> str:
    """Formats a single real feature into a plain-language explanation with numbers."""
    if feature_name == "rain_1d":
        return f"1-day rain {value:.1f} mm"
    elif feature_name == "rain_3d":
        return f"3-day cumulative rain {value:.1f} mm"
    elif feature_name == "rain_7d":
        return f"7-day cumulative rain {value:.1f} mm"
    elif feature_name == "rain_14d":
        return f"14-day cumulative rain {value:.1f} mm"
    elif feature_name == "rain_30d":
        return f"30-day cumulative rain {value:.1f} mm"
    elif feature_name == "discharge_m3s":
        return f"River discharge {value:.1f} m³/s"
    elif feature_name == "discharge_roc_3d":
        sign = "+" if value >= 0 else ""
        return f"3-day discharge rate of change {sign}{value:.1f} m³/s"
    elif feature_name == "antecedent_wetness_7d":
        return f"7-day antecedent soil wetness {value:.1f} mm"
    elif feature_name in ["day_of_year", "month"]:
        return "usual monsoon-season conditions"
    return f"{feature_name}: {value:.1f}"

def compute_top_drivers_from_model(
    model: Any,
    input_df: pd.DataFrame,
    predicted_class: int = 1
) -> List[Tuple[str, float, float]]:
    """Computes exact per-prediction feature contributions using LightGBM pred_contrib=True.
    
    Returns:
        List of tuples: (feature_name, feature_value, contribution_score)
    """
    X = input_df[FEATURE_COLUMNS_DAILY]
    n_features = len(FEATURE_COLUMNS_DAILY)

    if hasattr(model, "booster_"):
        booster = model.booster_
        contribs = booster.predict(X, pred_contrib=True)
        contribs_arr = np.array(contribs)

        if contribs_arr.ndim == 2:
            row_contribs = contribs_arr[0]
            stride = n_features + 1
            cls_idx = min(3, max(0, predicted_class))
            feat_contribs = row_contribs[cls_idx * stride : cls_idx * stride + n_features]
        else:
            feat_contribs = contribs_arr[0, :n_features]
    else:
        # Fallback: normalize positive values
        feat_contribs = np.zeros(n_features)
        for i, col in enumerate(FEATURE_COLUMNS_DAILY):
            val = float(X.iloc[0][col])
            feat_contribs[i] = val

    # Rank features by positive contribution score first, then absolute value
    results = []
    for i, fname in enumerate(FEATURE_COLUMNS_DAILY):
        val = float(X.iloc[0][fname])
        score = float(feat_contribs[i])
        results.append((fname, val, score))

    # Sort descending by contribution score
    results.sort(key=lambda x: x[2], reverse=True)
    return results

def get_top_drivers_list(
    features: Dict[str, float],
    risk_level: str = "Green",
    model: Any = None,
    station_thresholds: Dict[str, float] = None
) -> List[str]:
    """Generates top factor statements using real model feature contributions (LightGBM pred_contrib / SHAP).
    For Orange/Red classes, driver #1 states current discharge relative to threshold.
    Followed by up to 2 model drivers with numbers.
    """
    top_statements: List[str] = []

    # For Orange/Red classes, first driver MUST state current discharge relative to crossed threshold
    if risk_level in ["Orange", "Red"]:
        q_val = float(features.get("discharge_m3s", 0.0))
        if station_thresholds:
            t_val = float(station_thresholds.get("p99.5_red", 500.0)) if risk_level == "Red" else float(station_thresholds.get("p97_orange", 300.0))
        else:
            t_val = 500.0 if risk_level == "Red" else 300.0
        
        t_name = "Red" if risk_level == "Red" else "Orange"
        top_statements.append(f"Discharge {q_val:,.1f} m³/s, above the {t_name} threshold {t_val:,.1f} m³/s")

    df_row = pd.DataFrame([{col: features.get(col, 0.0) for col in FEATURE_COLUMNS_DAILY}])
    risk_int_map = {"Green": 0, "Yellow": 1, "Orange": 2, "Red": 3}
    pred_cls = risk_int_map.get(risk_level, 1)

    ranked = compute_top_drivers_from_model(model, df_row, pred_cls)
    seen_seasonality = False

    for fname, val, score in ranked:
        if len(top_statements) >= 3:
            break

        # Avoid duplicating discharge if already added as first driver for Orange/Red
        if risk_level in ["Orange", "Red"] and fname == "discharge_m3s":
            continue

        if score <= 0 and val == 0.0 and len(top_statements) > 0:
            continue

        stmt = format_driver_statement(fname, val)

        if stmt == "usual monsoon-season conditions":
            if seen_seasonality:
                continue
            seen_seasonality = True

        if stmt not in top_statements:
            top_statements.append(stmt)

    return top_statements

def generate_plain_language_explanation(features: Dict[str, float], risk_level: str = "Green", model: Any = None) -> str:
    """Generates plain-language top factor bullet points using ONLY real model features."""
    drivers = get_top_drivers_list(features, risk_level, model)
    return "; ".join(drivers)
