"""Feature Engineering Pipeline for Multi-Horizon Flood Risk Prediction.

Computes rolling hydrological features at time t (using ONLY data available up to time t)
and constructs true future target labels at time t+24h (and t+48h, t+72h) to eliminate data leakage.
"""

import pandas as pd
import numpy as np

FEATURE_COLUMNS = [
    "rain_sum_6h",
    "rain_sum_24h",
    "rain_sum_72h",
    "discharge_m3s",
    "discharge_rate_of_change_24h",
    "antecedent_wetness_index",
    "month",
    "day_of_year"
]

def build_features(df: pd.DataFrame, warning_threshold_discharge: float = 300.0, danger_threshold_discharge: float = 550.0, horizon_hours: int = 24) -> pd.DataFrame:
    """Calculates rolling hydrological features at time t and future target risk label at t + horizon_hours.
    
    Args:
        df: DataFrame containing 'timestamp', 'precipitation_mm', and 'river_discharge_m3s'.
        warning_threshold_discharge: Station warning discharge threshold (m³/s).
        danger_threshold_discharge: Station danger discharge threshold (m³/s).
        horizon_hours: Future prediction lead time in hours (default: 24h).

    Returns:
        DataFrame containing time-t feature columns and future target risk label at t + horizon_hours.
    """
    df = df.copy()
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

    precip = df["precipitation_mm"].fillna(0.0)
    discharge = df["river_discharge_m3s"].fillna(0.0)

    # 1. Features computed ONLY using data available up to time t
    df["rain_sum_6h"] = precip.rolling(window=6, min_periods=1).sum()
    df["rain_sum_24h"] = precip.rolling(window=24, min_periods=1).sum()
    df["rain_sum_72h"] = precip.rolling(window=72, min_periods=1).sum()

    df["discharge_m3s"] = discharge
    df["discharge_rate_of_change_24h"] = discharge.diff(periods=24).fillna(0.0)

    # Antecedent Precipitation Index (7-day exponential decay wetness proxy at time t)
    api_series = np.zeros(len(df))
    precip_vals = precip.values
    decay = 0.85
    for i in range(1, len(df)):
        api_series[i] = api_series[i-1] * decay + precip_vals[i]
    df["antecedent_wetness_index"] = api_series

    # Seasonality
    if "timestamp" in df.columns:
        df["month"] = df["timestamp"].dt.month
        df["day_of_year"] = df["timestamp"].dt.dayofyear
    else:
        df["month"] = 8
        df["day_of_year"] = 230

    # 2. Risk Label Assignment at current time t
    def derive_risk_at_time(d_val: float, r72_val: float) -> int:
        if d_val >= danger_threshold_discharge or r72_val >= 250.0:
            return 3 # Red
        elif d_val >= warning_threshold_discharge or r72_val >= 150.0:
            return 2 # Orange
        elif d_val >= (warning_threshold_discharge * 0.7) or r72_val >= 75.0:
            return 1 # Yellow
        else:
            return 0 # Green

    # Calculate current risk at time t
    df["current_risk_at_t"] = [
        derive_risk_at_time(d, r72) for d, r72 in zip(df["discharge_m3s"], df["rain_sum_72h"])
    ]

    # 3. FUTURE TARGET REDEFINITION (NO LEAKAGE): Target Y is risk level at time t + horizon_hours
    # Shift current risk backward by horizon_hours so row t contains target for t + horizon_hours
    df["target_risk_future"] = df["current_risk_at_t"].shift(-horizon_hours)

    # Drop rows at the tail end where future target is NaN due to shift
    df_valid = df.dropna(subset=["target_risk_future"]).copy()
    df_valid["target_risk_future"] = df_valid["target_risk_future"].astype(int)

    return df_valid
