"""Round 6D Raw Data Fetcher & Single Writer.

Fetches unmodified 1990-2025 daily discharge & rainfall data directly from Open-Meteo APIs,
saves raw JSONs to data/raw_api/, builds data/raw_api/manifest.json, and parses raw CSVs
into data/raw/ with ZERO arithmetic, scaling, smoothing, clipping or interpolation.
"""

import os
import sys
import json
import time
import hashlib
import requests
from datetime import datetime, timezone
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_API_DIR = os.path.join(DATA_DIR, "raw_api")
RAW_DIR = os.path.join(DATA_DIR, "raw")

os.makedirs(RAW_API_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

def compute_bytes_sha256(data_bytes: bytes) -> str:
    return hashlib.sha256(data_bytes).hexdigest()

def fetch_with_backoff(url: str, max_retries: int = 10, initial_delay: float = 2.0) -> bytes:
    """Fetches URL with exponential backoff up to 10 minutes on rate-limit / errors."""
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, timeout=30.0)
            if resp.status_code == 200:
                body_bytes = resp.content
                # Verify valid JSON
                data = json.loads(body_bytes.decode('utf-8'))
                if not data.get("error"):
                    return body_bytes
                else:
                    print(f"    [API Error] {data.get('reason')} (Attempt {attempt}/{max_retries})")
            elif resp.status_code == 429:
                print(f"    [Rate Limited 429] Waiting {delay:.1f}s backoff (Attempt {attempt}/{max_retries})...")
            else:
                print(f"    [HTTP {resp.status_code}] Attempt {attempt}/{max_retries}...")
        except Exception as e:
            print(f"    [Network Exception] {e} (Attempt {attempt}/{max_retries})...")
        
        if attempt < max_retries:
            time.sleep(delay)
            delay = min(600.0, delay * 2.0)

    raise RuntimeError(f"NOT DONE: Failed to fetch {url} after {max_retries} attempts.")

def main():
    print("=" * 110)
    print(" STEP 2: FETCHING UNMODIFIED RAW OPEN-METEO DATA (SINGLE WRITER TO data/raw/*.csv)")
    print("=" * 110)

    meta_path = os.path.join(DATA_DIR, "stations_metadata.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        stations_list = json.load(f)

    manifest = {}
    kerala_dfs = []
    assam_dfs = []

    print(f"{'Station ID':<12} {'Station Name':<15} {'Rows':<8} {'First Date':<12} {'Last Date':<12} {'Nulls Dropped':<15} {'Returned Lat/Lon'}")
    print("-" * 110)

    start_date = "1990-01-01"
    end_date = "2025-09-30"

    for st in stations_list:
        st_id = st["id"]
        st_name = st["name"]
        region = st["region"]
        lat = st.get("grid_cell_lat", st["latitude"])
        lon = st.get("grid_cell_lon", st["longitude"])

        flood_url = f"https://flood-api.open-meteo.com/v1/flood?latitude={lat}&longitude={lon}&daily=river_discharge&start_date={start_date}&end_date={end_date}"
        weather_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&daily=precipitation_sum&start_date={start_date}&end_date={end_date}"

        # 1. Fetch & Save Discharge JSON
        dis_bytes = fetch_with_backoff(flood_url)
        dis_json_path = os.path.join(RAW_API_DIR, f"{st_id}_discharge.json")
        with open(dis_json_path, "wb") as f:
            f.write(dis_bytes)

        dis_sha = compute_bytes_sha256(dis_bytes)
        dis_data = json.loads(dis_bytes.decode('utf-8'))
        dis_utc_now = datetime.now(timezone.utc).isoformat()

        # 2. Fetch & Save Rainfall JSON
        rain_bytes = fetch_with_backoff(weather_url)
        rain_json_path = os.path.join(RAW_API_DIR, f"{st_id}_rainfall.json")
        with open(rain_json_path, "wb") as f:
            f.write(rain_bytes)

        rain_sha = compute_bytes_sha256(rain_bytes)
        rain_data = json.loads(rain_bytes.decode('utf-8'))
        rain_utc_now = datetime.now(timezone.utc).isoformat()

        ret_lat_dis = dis_data.get("latitude", lat)
        ret_lon_dis = dis_data.get("longitude", lon)

        manifest[st_id] = {
            "discharge": {
                "url": flood_url,
                "fetch_time_utc": dis_utc_now,
                "sha256": dis_sha,
                "returned_lat": ret_lat_dis,
                "returned_lon": ret_lon_dis
            },
            "rainfall": {
                "url": weather_url,
                "fetch_time_utc": rain_utc_now,
                "sha256": rain_sha,
                "returned_lat": rain_data.get("latitude", lat),
                "returned_lon": rain_data.get("longitude", lon)
            }
        }

        # 3. Parse JSONs with NO arithmetic
        dis_times = dis_data.get("daily", {}).get("time", [])
        dis_vals = dis_data.get("daily", {}).get("river_discharge", [])

        rain_times = rain_data.get("daily", {}).get("time", [])
        rain_vals = rain_data.get("daily", {}).get("precipitation_sum", [])

        df_dis = pd.DataFrame({"date": dis_times, "river_discharge_m3s": dis_vals})
        df_rain = pd.DataFrame({"date": rain_times, "precipitation_sum_mm": rain_vals})

        df_merged = pd.merge(df_dis, df_rain, on="date", how="outer")
        df_merged["station_id"] = st_id

        # Count nulls dropped
        null_mask = df_merged["river_discharge_m3s"].isna() | df_merged["precipitation_sum_mm"].isna()
        nulls_dropped = int(null_mask.sum())

        df_clean = df_merged[~null_mask].copy()
        df_clean = df_clean.sort_values("date").reset_index(drop=True)

        # Save individual raw CSV
        csv_filename = f"{st_id}_1990_2025.csv"
        csv_path = os.path.join(RAW_DIR, csv_filename)
        df_clean.to_csv(csv_path, index=False)

        if region == "Kerala":
            kerala_dfs.append(df_clean)
        else:
            assam_dfs.append(df_clean)

        first_d = df_clean["date"].min() if not df_clean.empty else "N/A"
        last_d = df_clean["date"].max() if not df_clean.empty else "N/A"
        num_rows = len(df_clean)

        print(f"{st_id:<12} {st_name:<15} {num_rows:<8} {first_d:<12} {last_d:<12} {nulls_dropped:<15} ({ret_lat_dis}, {ret_lon_dis})")

    # Save manifest.json
    manifest_path = os.path.join(RAW_API_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Save regional CSVs
    if kerala_dfs:
        pd.concat(kerala_dfs, ignore_index=True).to_csv(os.path.join(RAW_DIR, "kerala_daily_1990_2025.csv"), index=False)
    if assam_dfs:
        pd.concat(assam_dfs, ignore_index=True).to_csv(os.path.join(RAW_DIR, "assam_daily_1990_2025.csv"), index=False)

    print("\n[Step 2 Complete] Raw JSONs saved to data/raw_api/ and unmodified CSVs saved to data/raw/!")

if __name__ == "__main__":
    main()
