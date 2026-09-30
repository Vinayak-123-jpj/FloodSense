"""Open-Meteo Historical Weather & Flood Data Fetcher.

Downloads real hourly precipitation (Weather API) and daily river discharge (Flood API)
for Kerala (August 2018 event and 2018-2023) and Assam (2020-2023).
Caches data into /data/raw/ as CSV files to ensure 100% offline functionality.
"""

import os
import json
import time
import requests
import pandas as pd

def fetch_open_meteo_data(lat: float, lon: float, start_date: str, end_date: str):
    """Fetches real weather precipitation and flood river discharge from Open-Meteo APIs."""
    print(f"[Fetch] Querying Open-Meteo for Lat {lat}, Lng {lon} from {start_date} to {end_date}...")
    
    # 1. Weather API (Hourly Precipitation)
    weather_url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=precipitation"
    )
    
    hourly_df = None
    try:
        res_w = requests.get(weather_url, timeout=15)
        if res_w.status_code == 200:
            w_data = res_w.json()
            if "hourly" in w_data:
                hourly_df = pd.DataFrame({
                    "timestamp": w_data["hourly"]["time"],
                    "precipitation_mm": w_data["hourly"]["precipitation"]
                })
                hourly_df["timestamp"] = pd.to_datetime(hourly_df["timestamp"])
    except Exception as e:
        print(f"[Warning] Weather API query failed: {e}")

    # 2. Flood API (Daily River Discharge)
    flood_url = (
        f"https://flood-api.open-meteo.com/v1/flood?"
        f"latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=river_discharge"
    )
    
    daily_df = None
    try:
        res_f = requests.get(flood_url, timeout=15)
        if res_f.status_code == 200:
            f_data = res_f.json()
            if "daily" in f_data:
                daily_df = pd.DataFrame({
                    "date": f_data["daily"]["time"],
                    "river_discharge_m3s": f_data["daily"]["river_discharge"]
                })
                daily_df["date"] = pd.to_datetime(daily_df["date"])
    except Exception as e:
        print(f"[Warning] Flood API query failed: {e}")

    # Combine hourly weather with daily discharge via forward fill
    if hourly_df is not None:
        if daily_df is not None:
            hourly_df["date"] = hourly_df["timestamp"].dt.floor("D")
            merged = pd.merge(hourly_df, daily_df, on="date", how="left")
            merged["river_discharge_m3s"] = merged["river_discharge_m3s"].ffill().bfill()
            merged = merged.drop(columns=["date"])
            return merged
        else:
            hourly_df["river_discharge_m3s"] = 0.0
            return hourly_df
            
    return None

def fetch_and_cache_all():
    """Fetches and commits historical datasets for primary stations in Kerala and Assam."""
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    metadata_path = os.path.join(os.path.dirname(__file__), "..", "data", "stations_metadata.json")
    with open(metadata_path, "r", encoding="utf-8") as f:
        stations = json.load(f)

    # 1. Fetch Kerala August 2018 historic flood window (Neeleswaram station)
    kerala_station = next(s for s in stations if s["id"] == "KL-PER-01")
    df_kerala = fetch_open_meteo_data(
        lat=kerala_station["latitude"],
        lon=kerala_station["longitude"],
        start_date="2018-01-01",
        end_date="2018-12-31"
    )

    if df_kerala is not None and not df_kerala.empty:
        df_kerala["station_id"] = "KL-PER-01"
        out_kerala = os.path.join(raw_dir, "kerala_weather_flood.csv")
        df_kerala.to_csv(out_kerala, index=False)
        print(f"[Fetch Success] Saved {len(df_kerala)} hourly rows to {out_kerala}")

    time.sleep(1)

    # 2. Fetch Assam 2020-2022 window (Guwahati station)
    assam_station = next(s for s in stations if s["id"] == "AS-BRA-01")
    df_assam = fetch_open_meteo_data(
        lat=assam_station["latitude"],
        lon=assam_station["longitude"],
        start_date="2020-01-01",
        end_date="2022-12-31"
    )

    if df_assam is not None and not df_assam.empty:
        df_assam["station_id"] = "AS-BRA-01"
        out_assam = os.path.join(raw_dir, "assam_weather_flood.csv")
        df_assam.to_csv(out_assam, index=False)
        print(f"[Fetch Success] Saved {len(df_assam)} hourly rows to {out_assam}")

if __name__ == "__main__":
    fetch_and_cache_all()
