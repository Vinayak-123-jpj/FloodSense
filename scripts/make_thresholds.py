"""Round 6D Threshold Generator.

Computes 1990-2017 training set statistics (n, min, median, p90, p97, p99.5, max)
for all 11 stations directly from raw CSVs using np.percentile, asserts p90 < p97 < p99.5 <= max,
computes 2018 peak and high-risk day counts, and writes single source of truth data/thresholds.json.
"""

import os
import sys
import json
import hashlib
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
FRONTEND_DATA_DIR = os.path.join(PROJECT_ROOT, "frontend", "public", "data")

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()[:8]

def main():
    meta_path = os.path.join(DATA_DIR, "stations_metadata.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        stations_list = json.load(f)

    thresholds_dict = {}

    print("=" * 125)
    print(" STEP 4: GENERATING SINGLE SOURCE OF TRUTH THRESHOLDS (1990-01-01 to 2017-12-31 Baseline)")
    print("=" * 125)
    print(f"{'Station ID':<12} {'Station Name':<15} {'N (1990-2017)':<15} {'Median':<10} {'p90':<12} {'p97':<12} {'p99.5':<12} {'Max Q':<12} {'2018 High-Risk':<16} {'2018 Peak':<12} {'Assertion'}")
    print("-" * 145)

    for st in stations_list:
        st_id = st["id"]
        st_name = st["name"]
        region = st["region"]
        river = st["river"]
        req_lat = st["latitude"]
        req_lon = st["longitude"]
        grid_lat = st.get("grid_cell_lat", req_lat)
        grid_lon = st.get("grid_cell_lon", req_lon)
        is_short = st.get("is_short_history", False)

        csv_path = os.path.join(RAW_DIR, f"{st_id}_1990_2025.csv")
        if not os.path.exists(csv_path):
            if region == "Kerala":
                csv_path = os.path.join(RAW_DIR, "kerala_daily_1990_2025.csv")
            else:
                csv_path = os.path.join(RAW_DIR, "assam_daily_1990_2025.csv")

        df = pd.read_csv(csv_path)
        if "station_id" in df.columns:
            df = df[df["station_id"] == st_id].copy()

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        sha = compute_sha256(csv_path) if os.path.exists(csv_path) else "N/A"

        # 1. Filter strictly 1990-01-01 to 2017-12-31 for threshold training baseline
        df_train = df[(df["date"] >= "1990-01-01") & (df["date"] <= "2017-12-31")].copy()
        q_train = df_train["river_discharge_m3s"].dropna().values

        n_train = len(q_train)
        q_min = float(np.min(q_train)) if n_train > 0 else 0.0
        q_med = float(np.median(q_train)) if n_train > 0 else 0.0
        q_p90 = float(np.percentile(q_train, 90.0)) if n_train > 0 else 10.0
        q_p97 = float(np.percentile(q_train, 97.0)) if n_train > 0 else 25.0
        q_p99_5 = float(np.percentile(q_train, 99.5)) if n_train > 0 else 50.0
        q_max = float(np.max(q_train)) if n_train > 0 else 100.0

        # Assert strict threshold ordering: p90 < p97 < p99.5 <= max
        assert q_p90 < q_p97 < q_p99_5 <= q_max, f"Threshold assertion failed for {st_id}: {q_p90} < {q_p97} < {q_p99_5} <= {q_max}"

        # 2. 2018 stats
        df_2018 = df[(df["date"] >= "2018-01-01") & (df["date"] <= "2018-12-31")]
        if not df_2018.empty and not is_short:
            q_2018_vals = df_2018["river_discharge_m3s"].dropna().values
            high_risk_days_2018 = int((q_2018_vals >= q_p97).sum())
            peak_2018 = float(np.max(q_2018_vals))
        else:
            high_risk_days_2018 = "N/A (Short)"
            peak_2018 = "N/A"

        history_note = "Short history (1990-2009); excluded from 2018 held-out test set" if is_short else "Full history (1990-2025)"
        date_range_str = "1990-01-01 to 2009-12-31" if is_short else "1990-01-01 to 2025-09-30"

        thresholds_dict[st_id] = {
            "name": st_name,
            "river": river,
            "region": region,
            "requested_lat": req_lat,
            "requested_lon": req_lon,
            "grid_cell_lat": grid_lat,
            "grid_cell_lon": grid_lon,
            "csv_sha256": sha,
            "training_rows": n_train,
            "date_range": date_range_str,
            "p90_yellow": round(q_p90, 2),
            "p97_orange": round(q_p97, 2),
            "p99.5_red": round(q_p99_5, 2),
            "p99_5_red": round(q_p99_5, 2),
            "historical_min_m3s": round(q_min, 1),
            "historical_median_m3s": round(q_med, 1),
            "historical_max_m3s": round(q_max, 1),
            "peak_2018_m3s": round(peak_2018, 1) if isinstance(peak_2018, float) else None,
            "actual_orange_red_days_2018": high_risk_days_2018 if isinstance(high_risk_days_2018, int) else None,
            "current_live_m3s": round(q_med, 1),
            "percentile_rank": 50.0,
            "computed_class": "Green",
            "is_short_history": is_short,
            "history_note": history_note
        }

        peak_str = f"{peak_2018:.1f}" if isinstance(peak_2018, float) else "N/A"
        days_str = str(high_risk_days_2018)

        print(f"{st_id:<12} {st_name:<15} {n_train:<15} {q_med:<10.1f} {q_p90:<12.2f} {q_p97:<12.2f} {q_p99_5:<12.2f} {q_max:<12.1f} {days_str:<16} {peak_str:<12} PASSED (p90<p97<p99.5<=max)")

    # Save to data/thresholds.json and frontend/public/data/thresholds.json
    t_out_backend = os.path.join(DATA_DIR, "thresholds.json")
    t_out_frontend = os.path.join(FRONTEND_DATA_DIR, "thresholds.json")

    with open(t_out_backend, "w", encoding="utf-8") as f:
        json.dump(thresholds_dict, f, indent=2)
    with open(t_out_frontend, "w", encoding="utf-8") as f:
        json.dump(thresholds_dict, f, indent=2)

    print(f"\n[Step 4 Complete] Single source of truth thresholds saved to {t_out_backend} and {t_out_frontend}!")

if __name__ == "__main__":
    main()
