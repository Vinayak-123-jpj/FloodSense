"""Round 6D Independent Verification Script.

Uses ONLY standard libraries, requests, pandas, and numpy.
Imports NO project modules (no backend/, no scripts/).

Re-fetches fresh daily discharge telemetry for all 11 stations directly from Open-Meteo flood API,
saves to data/truth/<station_id>.csv, compares value-by-value with data/raw/,
prints verification table, writes reports/verify_truth.txt, and exits non-zero if any mismatch occurs.
"""

import os
import sys
import json
import time
import requests
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
TRUTH_DIR = os.path.join(DATA_DIR, "truth")
RAW_DIR = os.path.join(DATA_DIR, "raw")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")

os.makedirs(TRUTH_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def fetch_fresh_truth(url: str, max_retries: int = 10, initial_delay: float = 2.0) -> dict:
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, timeout=30.0)
            if resp.status_code == 200:
                data = resp.json()
                if not data.get("error"):
                    return data
            elif resp.status_code == 429:
                time.sleep(delay)
                delay = min(600.0, delay * 2.0)
        except Exception:
            time.sleep(delay)
            delay = min(600.0, delay * 2.0)
    raise RuntimeError(f"Failed fresh truth fetch for {url}")

def main():
    meta_path = os.path.join(DATA_DIR, "stations_metadata.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        stations_list = json.load(f)

    start_date = "1990-01-01"
    end_date = "2025-09-30"

    table_lines = []
    header_str = f"{'Station ID':<12} {'Station Name':<15} {'Rows':<8} {'Max Abs Diff':<15} {'Dates Equal?':<15} {'Verification Status'}"
    sep_str = "-" * 90

    table_lines.append("=" * 90)
    table_lines.append(" STEP 3: INDEPENDENT DATA TRUTH VERIFICATION (data/truth/ vs data/raw/)")
    table_lines.append("=" * 90)
    table_lines.append(header_str)
    table_lines.append(sep_str)

    print("\n".join(table_lines[:4]))
    print(sep_str)

    all_passed = True

    for st in stations_list:
        st_id = st["id"]
        st_name = st["name"]
        lat = st.get("grid_cell_lat", st["latitude"])
        lon = st.get("grid_cell_lon", st["longitude"])

        url = f"https://flood-api.open-meteo.com/v1/flood?latitude={lat}&longitude={lon}&daily=river_discharge&start_date={start_date}&end_date={end_date}"
        truth_json = fetch_fresh_truth(url)

        times = truth_json.get("daily", {}).get("time", [])
        discharges = truth_json.get("daily", {}).get("river_discharge", [])

        df_truth = pd.DataFrame({"date": times, "river_discharge_m3s": discharges})
        df_truth = df_truth.dropna(subset=["river_discharge_m3s"]).reset_index(drop=True)

        truth_csv_path = os.path.join(TRUTH_DIR, f"{st_id}.csv")
        df_truth.to_csv(truth_csv_path, index=False)

        raw_csv_path = os.path.join(RAW_DIR, f"{st_id}_1990_2025.csv")
        if not os.path.exists(raw_csv_path):
            line = f"{st_id:<12} {st_name:<15} {'0':<8} {'N/A':<15} {'No':<15} FAILED (raw CSV missing)"
            table_lines.append(line)
            print(line)
            all_passed = False
            continue

        df_raw = pd.read_csv(raw_csv_path)

        # Merge on date for exact alignment
        df_merged = pd.merge(df_truth, df_raw, on="date", suffixes=("_truth", "_raw"))

        dates_equal = (len(df_merged) == len(df_truth)) and (len(df_merged) == len(df_raw))
        abs_diffs = np.abs(df_merged["river_discharge_m3s_truth"].values - df_merged["river_discharge_m3s_raw"].values)
        max_abs_diff = float(np.max(abs_diffs)) if len(abs_diffs) > 0 else 99999.0

        status = "PASSED (EXACT MATCH 0.0)" if (dates_equal and max_abs_diff == 0.0) else "FAILED (MISMATCH)"
        if not (dates_equal and max_abs_diff == 0.0):
            all_passed = False

        dates_str = "Yes" if dates_equal else "No"
        line = f"{st_id:<12} {st_name:<15} {len(df_merged):<8} {max_abs_diff:<15.6f} {dates_str:<15} {status}"
        table_lines.append(line)
        print(line)

    # Save to reports/verify_truth.txt
    txt_path = os.path.join(REPORTS_DIR, "verify_truth.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(table_lines) + "\n")

    print(f"\nVerification table written to {txt_path}")

    if not all_passed:
        print("\n[Step 3 FAILED] Data truth mismatch detected!")
        sys.exit(1)
    else:
        print("\n[Step 3 PASSED] All 11 stations matched data/truth/ with max abs diff = 0.0!")

if __name__ == "__main__":
    main()
