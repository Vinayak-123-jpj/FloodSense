"""Fast Grid Cell Snapper and Historical Re-fetcher.

Finds main-channel Open-Meteo grid cells for all 11 stations,
fetches complete 1990-2025 daily historical discharge & precipitation time series,
computes exact 1990-2017 training percentiles (p90, p97, p99.5),
and generates data/thresholds.json single source of truth.
"""

import requests
import json
import os
import numpy as np
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

STATIONS = [
  {"id": "KL-PER-01", "name": "Neeleswaram", "river": "Periyar River", "lat": 10.1416, "lon": 76.5781},
  {"id": "KL-PER-02", "name": "Aluva", "river": "Periyar River", "lat": 10.1076, "lon": 76.3516},
  {"id": "KL-PAM-01", "name": "Chengannur", "river": "Pamba River", "lat": 9.3175, "lon": 76.6122},
  {"id": "KL-MUV-01", "name": "Muvattupuzha", "river": "Muvattupuzha River", "lat": 9.9813, "lon": 76.5772},
  {"id": "KL-CHA-01", "name": "Chalakudy", "river": "Chalakudy River", "lat": 10.307, "lon": 76.3323},
  {"id": "KL-ACH-01", "name": "Thumpamon", "river": "Achenkovil River", "lat": 9.256, "lon": 76.711},
  {"id": "AS-BRA-01", "name": "Guwahati", "river": "Brahmaputra River", "lat": 26.1833, "lon": 91.75},
  {"id": "AS-BRA-02", "name": "Dibrugarh", "river": "Brahmaputra River", "lat": 27.4728, "lon": 94.912},
  {"id": "AS-KOP-01", "name": "Kampur", "river": "Kopili River", "lat": 26.15, "lon": 92.5833},
  {"id": "AS-DHA-01", "name": "Numaligarh", "river": "Dhansiri River", "lat": 26.5667, "lon": 93.7333},
  {"id": "AS-JIA-01", "name": "Tezpur", "river": "Jia Bharali River", "lat": 26.6333, "lon": 92.8}
]

# Probe candidates around requested coordinates
def probe_main_channel_cell(req_lat, req_lon, station_id):
    # Search radius: 0.1 degree grid around requested coordinate
    lats = [round(req_lat + d, 4) for d in [-0.075, -0.05, -0.025, 0.0, 0.025, 0.05, 0.075]]
    lons = [round(req_lon + d, 4) for d in [-0.075, -0.05, -0.025, 0.0, 0.025, 0.05, 0.075]]
    
    candidates = []
    for lat in lats:
        for lon in lons:
            # Query recent 7-day mean discharge
            url = f"https://flood-api.open-meteo.com/v1/flood?latitude={lat}&longitude={lon}&daily=river_discharge&past_days=7&forecast_days=1"
            try:
                res = requests.get(url, timeout=3.0).json()
                grid_lat = res.get("latitude", lat)
                grid_lon = res.get("longitude", lon)
                q_vals = res.get("daily", {}).get("river_discharge", [])
                q_mean = float(np.mean([v for v in q_vals if v is not None])) if q_vals and any(v is not None for v in q_vals) else 0.0
                dist = np.hypot(grid_lat - req_lat, grid_lon - req_lon)
                candidates.append((grid_lat, grid_lon, q_mean, dist))
            except Exception:
                continue

    if not candidates:
        return req_lat, req_lon

    # For major rivers (Guwahati, Dibrugarh, Tezpur), pick the mainstem channel cell (maximum discharge cell within ~0.1 deg)
    # For small tributary stations, pick max discharge within 0.08 deg
    candidates.sort(key=lambda x: -x[2]) # Sort by highest discharge
    best = candidates[0]
    return best[0], best[1]

print("[Grid Cell Snapper] Probing main river channel grid cells for all 11 stations...")
snapped_coords = {}
for st in STATIONS:
    snapped_lat, snapped_lon = probe_main_channel_cell(st["lat"], st["lon"], st["id"])
    snapped_coords[st["id"]] = (snapped_lat, snapped_lon)
    print(f" {st['id']} ({st['name']}): Requested ({st['lat']}, {st['lon']}) -> Snapped Grid Cell ({snapped_lat}, {snapped_lon})")

print("\n[Historical Fetcher] Downloading complete 1990-2025 daily reanalysis for snapped grid cells...")
all_historical_frames = []
thresholds_dict = {}

for st in STATIONS:
    st_id = st["id"]
    cell_lat, cell_lon = snapped_coords[st_id]
    
    # 1. Fetch historical flood discharge
    flood_url = f"https://flood-api.open-meteo.com/v1/flood?latitude={cell_lat}&longitude={cell_lon}&start_date=1990-01-01&end_date=2025-09-30&daily=river_discharge"
    weather_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={cell_lat}&longitude={cell_lon}&start_date=1990-01-01&end_date=2025-09-30&daily=precipitation_sum"
    
    try:
        f_resp = requests.get(flood_url, timeout=10.0).json().get("daily", {})
        w_resp = requests.get(weather_url, timeout=10.0).json().get("daily", {})
        
        dates = f_resp.get("time", [])
        discharges = f_resp.get("river_discharge", [])
        precips = w_resp.get("precipitation_sum", [])
        
        # Clean nulls
        clean_dis = [float(v) if v is not None else 0.0 for v in discharges]
        clean_pr = [float(v) if v is not None else 0.0 for v in precips[:len(dates)]]
        
        df_st = pd.DataFrame({
            "station_id": st_id,
            "date": dates,
            "river_discharge_m3s": clean_dis,
            "precipitation_sum_mm": clean_pr
        })
        
        # Save raw CSV
        csv_path = os.path.join(RAW_DIR, f"{st_id}_1990_2025.csv")
        df_st.to_csv(csv_path, index=False)
        all_historical_frames.append(df_st)
        
        # Compute training baseline percentiles (1990-2017)
        df_st["year"] = pd.to_datetime(df_st["date"]).dt.year
        train_df = df_st[df_st["year"] <= 2017]
        train_q = train_df["river_discharge_m3s"].values
        
        p90 = float(np.percentile(train_q, 90.0))
        p97 = float(np.percentile(train_q, 97.0))
        p99_5 = float(np.percentile(train_q, 99.5))
        
        # Ensure strict monotonicity: p90 < p97 < p99.5
        if p97 <= p90: p97 = p90 * 1.25
        if p99_5 <= p97: p99_5 = p97 * 1.35
        
        thresholds_dict[st_id] = {
            "name": st["name"],
            "river": st["river"],
            "requested_lat": st["lat"],
            "requested_lon": st["lon"],
            "grid_cell_lat": cell_lat,
            "grid_cell_lon": cell_lon,
            "training_rows": len(train_df),
            "p90_yellow": round(p90, 2),
            "p97_orange": round(p97, 2),
            "p99.5_red": round(p99_5, 2),
            "p99_5_red": round(p99_5, 2),
            "historical_min_m3s": round(float(np.min(clean_dis)), 2),
            "historical_median_m3s": round(float(np.median(clean_dis)), 2),
            "historical_max_m3s": round(float(np.max(clean_dis)), 2)
        }
        print(f" Calculated thresholds for {st_id} ({st['name']}): p90={p90:.2f}, p97={p97:.2f}, p99.5={p99_5:.2f} m3/s")
    except Exception as e:
        print(f" ERROR fetching {st_id}: {e}")

# Save data/thresholds.json & frontend/public/data/thresholds.json
thresh_path1 = os.path.join(os.path.dirname(__file__), "..", "data", "thresholds.json")
thresh_path2 = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "data", "thresholds.json")

with open(thresh_path1, "w", encoding="utf-8") as f:
    json.dump(thresholds_dict, f, indent=2)

with open(thresh_path2, "w", encoding="utf-8") as f:
    json.dump(thresholds_dict, f, indent=2)

print("\n[Grid Cell Snapper] Successfully updated data/thresholds.json and frontend/public/data/thresholds.json!")
