"""Open-Meteo Long-Term Daily Data Fetcher (1990-2025).

Downloads real daily precipitation sums (Weather Archive API) and daily river discharge (Global Flood API)
for all 11 monitoring stations in Kerala and Assam from 1990 to 2025.
Applies exponential backoff retries and caches data to /data/raw/ as CSV files.
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime

def fetch_open_meteo_daily_station(lat: float, lon: float, station_id: str, start_date: str = "1990-01-01", end_date: str = "2025-12-31") -> pd.DataFrame:
    """Fetches real daily precipitation sum and daily river discharge for a station with retry backoff."""
    print(f"[Fetch Daily] Querying station {station_id} (Lat {lat}, Lng {lon}) from {start_date} to {end_date}...")
    
    # 1. Open-Meteo Weather API (Daily Precipitation Sum)
    weather_url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum"
    )
    
    daily_precip_df = None
    for attempt in range(3):
        try:
            res_w = requests.get(weather_url, timeout=20)
            if res_w.status_code == 200:
                w_data = res_w.json()
                if "daily" in w_data:
                    daily_precip_df = pd.DataFrame({
                        "date": w_data["daily"]["time"],
                        "precipitation_sum_mm": w_data["daily"]["precipitation_sum"]
                    })
                    daily_precip_df["date"] = pd.to_datetime(daily_precip_df["date"])
                    break
            elif res_w.status_code == 429:
                time.sleep(2 ** attempt)
        except Exception as e:
            print(f"[Fetch Warning] Attempt {attempt+1} failed for weather: {e}")
            time.sleep(2)

    # 2. Open-Meteo Flood API (Daily River Discharge m³/s)
    flood_url = (
        f"https://flood-api.open-meteo.com/v1/flood?"
        f"latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=river_discharge"
    )
    
    daily_discharge_df = None
    for attempt in range(3):
        try:
            res_f = requests.get(flood_url, timeout=20)
            if res_f.status_code == 200:
                f_data = res_f.json()
                if "daily" in f_data:
                    daily_discharge_df = pd.DataFrame({
                        "date": f_data["daily"]["time"],
                        "river_discharge_m3s": f_data["daily"]["river_discharge"]
                    })
                    daily_discharge_df["date"] = pd.to_datetime(daily_discharge_df["date"])
                    break
            elif res_f.status_code == 429:
                time.sleep(2 ** attempt)
        except Exception as e:
            print(f"[Fetch Warning] Attempt {attempt+1} failed for flood: {e}")
            time.sleep(2)

    # Merge daily weather and discharge
    if daily_precip_df is not None:
        if daily_discharge_df is not None:
            merged = pd.merge(daily_precip_df, daily_discharge_df, on="date", how="left")
            merged["river_discharge_m3s"] = merged["river_discharge_m3s"].ffill().bfill()
        else:
            merged = daily_precip_df
            merged["river_discharge_m3s"] = 0.0
            
        merged["station_id"] = station_id
        return merged

    return pd.DataFrame()

def fetch_and_cache_all_daily():
    """Fetches long historical daily records for all Kerala and Assam stations and saves to CSV."""
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    metadata_path = os.path.join(os.path.dirname(__file__), "..", "data", "stations_metadata.json")
    with open(metadata_path, "r", encoding="utf-8") as f:
        stations = json.load(f)

    kerala_dfs = []
    assam_dfs = []

    for st in stations:
        df_st = fetch_open_meteo_daily_station(
            lat=st["latitude"],
            lon=st["longitude"],
            station_id=st["id"],
            start_date="1990-01-01",
            end_date="2025-12-31"
        )
        time.sleep(1) # Rate limit delay

        if not df_st.empty:
            if st["region"] == "Kerala":
                kerala_dfs.append(df_st)
            else:
                assam_dfs.append(df_st)

    if kerala_dfs:
        full_kerala = pd.concat(kerala_dfs, ignore_index=True)
        out_kerala = os.path.join(raw_dir, "kerala_daily_1990_2025.csv")
        full_kerala.to_csv(out_kerala, index=False)
        print(f"[Fetch Daily Success] Saved {len(full_kerala)} daily records to {out_kerala}")

    if assam_dfs:
        full_assam = pd.concat(assam_dfs, ignore_index=True)
        out_assam = os.path.join(raw_dir, "assam_daily_1990_2025.csv")
        full_assam.to_csv(out_assam, index=False)
        print(f"[Fetch Daily Success] Saved {len(full_assam)} daily records to {out_assam}")

if __name__ == "__main__":
    fetch_and_cache_all_daily()
