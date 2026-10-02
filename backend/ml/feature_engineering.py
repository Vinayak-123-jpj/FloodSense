"""Daily Resolution Feature Engineering & Station-Percentile Risk Labeling.

Computes daily rolling rainfall sums (1d, 3d, 7d, 14d, 30d), discharge rate of change,
and 7-day antecedent precipitation index (API) at daily resolution.
Assigns risk labels using station-specific training period discharge percentiles (p90=Yellow, p97=Orange, p99.5=Red).
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple

FEATURE_COLUMNS_DAILY = [
    "rain_1d",
    "rain_3d",
    "rain_7d",
    "rain_14d",
    "rain_30d",
    "discharge_m3s",
    "discharge_roc_3d",
    "antecedent_wetness_7d",
    "month",
    "day_of_year"
]

# Backward compatibility alias
FEATURE_COLUMNS = FEATURE_COLUMNS_DAILY

def compute_station_percentiles(train_df: pd.DataFrame = None) -> Dict[str, Dict[str, float]]:
    """Loads thresholds from data/thresholds.json if available, else calculates from train_df."""
    import os, json
    thresholds_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "thresholds.json"))
    if os.path.exists(thresholds_path):
        with open(thresholds_path, "r", encoding="utf-8") as f:
            t_json = json.load(f)
        res = {}
        for st_id, info in t_json.items():
            res[st_id] = {
                "p90_yellow": float(info["p90_yellow"]),
                "p97_orange": float(info["p97_orange"]),
                "p99.5_red": float(info.get("p99.5_red", info.get("p99_5_red"))),
            }
        return res

    station_thresholds = {}
    if train_df is not None:
        for st_id, group in train_df.groupby("station_id"):
            d = group["river_discharge_m3s"].dropna()
            if len(d) > 0:
                p90 = float(np.percentile(d, 90))
                p97 = float(np.percentile(d, 97))
                p99_5 = float(np.percentile(d, 99.5))
            else:
                p90, p97, p99_5 = 100.0, 250.0, 500.0
            station_thresholds[st_id] = {
                "p90_yellow": p90,
                "p97_orange": p97,
                "p99.5_red": p99_5
            }
    return station_thresholds

def build_daily_features(
    df: pd.DataFrame,
    station_thresholds: Dict[str, Dict[str, float]] = None,
    horizon_days: int = 1
) -> pd.DataFrame:
    """Builds daily features and future risk target at day t + horizon_days.
    
    Args:
        df: Daily DataFrame containing 'date', 'precipitation_sum_mm', 'river_discharge_m3s', and 'station_id'.
        station_thresholds: Dict mapping station_id to discharge percentile thresholds.
        horizon_days: Prediction lead time in days (1, 2, or 3 days).

    Returns:
        DataFrame with daily features and shifted future target label.
    """
    df = df.copy()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(["station_id", "date"]).reset_index(drop=True)

    if station_thresholds is None:
        station_thresholds = compute_station_percentiles()

    station_dfs = []
    for st_id, group in df.groupby("station_id"):
        st_group = group.copy().sort_values("date").reset_index(drop=True)
        precip = st_group["precipitation_sum_mm"].fillna(0.0)
        discharge = st_group["river_discharge_m3s"].fillna(0.0)

        # 1. Rolling rainfall sums at daily resolution
        st_group["rain_1d"] = precip
        st_group["rain_3d"] = precip.rolling(window=3, min_periods=1).sum()
        st_group["rain_7d"] = precip.rolling(window=7, min_periods=1).sum()
        st_group["rain_14d"] = precip.rolling(window=14, min_periods=1).sum()
        st_group["rain_30d"] = precip.rolling(window=30, min_periods=1).sum()

        # 2. Discharge & Rate of Change
        st_group["discharge_m3s"] = discharge
        st_group["discharge_roc_3d"] = discharge.diff(periods=3).fillna(0.0)

        # 3. Antecedent Wetness Index (7-day decay)
        api_series = np.zeros(len(st_group))
        precip_vals = precip.values
        decay = 0.85
        for i in range(1, len(st_group)):
            api_series[i] = api_series[i-1] * decay + precip_vals[i]
        st_group["antecedent_wetness_7d"] = api_series

        # 4. Seasonality
        st_group["month"] = st_group["date"].dt.month
        st_group["day_of_year"] = st_group["date"].dt.dayofyear

        # 5. Station-specific Risk Label at Day t (using strict discharge percentiles)
        p_dict = station_thresholds.get(st_id, {})
        p90 = p_dict.get("p90_yellow", 100.0)
        p97 = p_dict.get("p97_orange", 250.0)
        p99_5 = p_dict.get("p99.5_red", p_dict.get("p99_5_red", 500.0))

        def derive_risk(d_val: float) -> int:
            if d_val >= p99_5:
                return 3 # Red
            elif d_val >= p97:
                return 2 # Orange
            elif d_val >= p90:
                return 1 # Yellow
            else:
                return 0 # Green

        st_group["current_risk_at_t"] = [derive_risk(d) for d in st_group["discharge_m3s"]]

        # 6. Future Target Shift by horizon_days (No Leakage)
        st_group[f"target_risk_{horizon_days}d"] = st_group["current_risk_at_t"].shift(-horizon_days)
        st_valid = st_group.dropna(subset=[f"target_risk_{horizon_days}d"]).copy()
        st_valid[f"target_risk_{horizon_days}d"] = st_valid[f"target_risk_{horizon_days}d"].astype(int)

        station_dfs.append(st_valid)

    if station_dfs:
        return pd.concat(station_dfs, ignore_index=True)
    return pd.DataFrame()

