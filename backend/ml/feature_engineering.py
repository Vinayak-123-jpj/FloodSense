"""Feature Engineering Pipeline for Flood Risk Classification.

Computes hydrological rolling rainfall windows (6h, 24h, 72h), river discharge rates of change,
antecedent precipitation index (API), and seasonal features from time-series sensor data.
"""

import pandas as pd
import numpy as np

def build_features(df: pd.DataFrame, warning_threshold_discharge: float = 300.0, danger_threshold_discharge: float = 550.0) -> pd.DataFrame:
    """Calculates rolling hydrological features and target risk labels from raw telemetry/weather data.
    
    Args:
        df: DataFrame containing 'timestamp', 'precipitation_mm', and 'river_discharge_m3s'.
        warning_threshold_discharge: Station warning discharge threshold (m³/s).
        danger_threshold_discharge: Station danger discharge threshold (m³/s).

    Returns:
        DataFrame populated with feature columns and target risk class label.
    """
    df = df.copy()
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

    precip = df["precipitation_mm"].fillna(0.0)
    discharge = df["river_discharge_m3s"].fillna(0.0)

    # 1. Rolling rainfall sums
    df["rain_sum_6h"] = precip.rolling(window=6, min_periods=1).sum()
    df["rain_sum_24h"] = precip.rolling(window=24, min_periods=1).sum()
    df["rain_sum_72h"] = precip.rolling(window=72, min_periods=1).sum()

    # 2. Discharge rate of change (24h delta)
    df["discharge_m3s"] = discharge
    df["discharge_rate_of_change_24h"] = discharge.diff(periods=24).fillna(0.0)

    # 3. Antecedent Precipitation Index (7-day exponential decay wetness proxy)
    api_series = np.zeros(len(df))
    precip_vals = precip.values
    decay = 0.85
    for i in range(1, len(df)):
        api_series[i] = api_series[i-1] * decay + precip_vals[i]
    df["antecedent_wetness_index"] = api_series

    # 4. Seasonality
    if "timestamp" in df.columns:
        df["month"] = df["timestamp"].dt.month
        df["day_of_year"] = df["timestamp"].dt.dayofyear
    else:
        df["month"] = 8  # Default monsoon month
        df["day_of_year"] = 230

    # 5. Risk Label Assignment (0=Green, 1=Yellow, 2=Orange, 3=Red)
    # Calibrated relative to station discharge and heavy 72h precipitation
    def derive_label(row):
        d = row["discharge_m3s"]
        r72 = row["rain_sum_72h"]
        if d >= danger_threshold_discharge or r72 >= 250.0:
            return 3 # Red
        elif d >= warning_threshold_discharge or r72 >= 150.0:
            return 2 # Orange
        elif d >= (warning_threshold_discharge * 0.7) or r72 >= 75.0:
            return 1 # Yellow
        else:
            return 0 # Green

    df["risk_label"] = df.apply(derive_label, axis=1)
    return df

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
