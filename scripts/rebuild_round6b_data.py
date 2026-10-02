"""Rebuild Round 6B Hydrological Dataset with Corrected Brahmaputra Mainstem Grid Cells.

1. Updates Guwahati (AS-BRA-01) and Dibrugarh (AS-BRA-02) grid cells to mainstem Brahmaputra channels:
   - AS-BRA-01 (Guwahati): requested_lat=26.2333, requested_lon=91.7500 -> grid_cell (26.2250, 91.7750)
   - AS-BRA-02 (Dibrugarh): requested_lat=27.4228, requested_lon=94.7120 -> grid_cell (27.4250, 94.7250)
2. Fetches 1990-2024 daily reanalysis history directly from Open-Meteo API.
3. Computes 1990-2017 training percentiles (min, median, p90, p97, p99.5, max, 2018 peak, SHA256).
4. Updates data/thresholds.json, frontend/public/data/thresholds.json, and data/stations_metadata.json.
"""

import os
import json
import hashlib
import requests
import numpy as np
import pandas as pd
import urllib3
import random
import time
from datetime import datetime
from typing import Dict, List, Tuple

urllib3.disable_warnings()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# Station definitions with corrected Brahmaputra mainstem coordinates
STATIONS_CONFIG = [
    {
        "id": "KL-PER-01", "name": "Neeleswaram", "river": "Periyar River", "region": "Kerala",
        "requested_lat": 10.1416, "requested_lon": 76.5781, "elevation_m": 12.0,
        "warning_level_m": 4.5, "danger_level_m": 6.0, "normal_level_m": 2.1,
        "description": "Periyar River upper gauging station monitoring upstream reservoir discharges."
    },
    {
        "id": "KL-PER-02", "name": "Aluva", "river": "Periyar River", "region": "Kerala",
        "requested_lat": 10.1076, "requested_lon": 76.3516, "elevation_m": 8.0,
        "warning_level_m": 3.8, "danger_level_m": 5.2, "normal_level_m": 1.8,
        "description": "Lower Periyar mainstem station near Ernakulam district intake points."
    },
    {
        "id": "KL-PAM-01", "name": "Chengannur", "river": "Pamba River", "region": "Kerala",
        "requested_lat": 9.3175, "requested_lon": 76.6122, "elevation_m": 14.0,
        "warning_level_m": 4.0, "danger_level_m": 5.5, "normal_level_m": 1.9,
        "description": "Central Pamba basin monitoring node covering Sabarimala pilgrimage corridor."
    },
    {
        "id": "KL-MUV-01", "name": "Muvattupuzha", "river": "Muvattupuzha River", "region": "Kerala",
        "requested_lat": 9.9813, "requested_lon": 76.5772, "elevation_m": 15.0,
        "warning_level_m": 3.5, "danger_level_m": 4.8, "normal_level_m": 1.5,
        "description": "Confluence gauging station downstream of Thodupuzha and Kothamangalam rivers."
    },
    {
        "id": "KL-CHA-01", "name": "Chalakudy", "river": "Chalakudy River", "region": "Kerala",
        "requested_lat": 10.3070, "requested_lon": 76.3323, "elevation_m": 10.0,
        "warning_level_m": 4.2, "danger_level_m": 5.8, "normal_level_m": 2.0,
        "description": "Chalakudy basin key gauging node monitoring Sholayar & Poringalkuthu dam releases."
    },
    {
        "id": "KL-ACH-01", "name": "Thumpamon", "river": "Achenkovil River", "region": "Kerala",
        "requested_lat": 9.2560, "requested_lon": 76.7110, "elevation_m": 18.0,
        "warning_level_m": 3.2, "danger_level_m": 4.5, "normal_level_m": 1.4,
        "description": "Upper Achenkovil river basin station monitoring flash flood surges."
    },
    # Corrected Brahmaputra mainstem coordinates (probed within ±0.25°)
    {
        "id": "AS-BRA-01", "name": "Guwahati", "river": "Brahmaputra River", "region": "Assam",
        "requested_lat": 26.2333, "requested_lon": 91.7500, "elevation_m": 55.0,
        "warning_level_m": 48.5, "danger_level_m": 49.7, "normal_level_m": 44.0,
        "description": "Brahmaputra mainstem gauging station monitoring Kamrup urban inundation risks."
    },
    {
        "id": "AS-BRA-02", "name": "Dibrugarh", "river": "Brahmaputra River", "region": "Assam",
        "requested_lat": 27.4228, "requested_lon": 94.7120, "elevation_m": 104.0,
        "warning_level_m": 104.5, "danger_level_m": 105.7, "normal_level_m": 100.0,
        "description": "Upper Assam Brahmaputra mainstem station tracking surge from Arunachal catchment."
    },
    {
        "id": "AS-KOP-01", "name": "Kampur", "river": "Kopili River", "region": "Assam",
        "requested_lat": 26.1500, "requested_lon": 92.5833, "elevation_m": 60.0,
        "warning_level_m": 59.0, "danger_level_m": 60.5, "normal_level_m": 54.0,
        "description": "Nagaon district Kopili river station monitoring Karbi Anglong hill discharges."
    },
    {
        "id": "AS-DHA-01", "name": "Numaligarh", "river": "Dhansiri River", "region": "Assam",
        "requested_lat": 26.5667, "requested_lon": 93.7333, "elevation_m": 76.0,
        "warning_level_m": 76.5, "danger_level_m": 77.4, "normal_level_m": 71.0,
        "description": "Golaghat district Dhansiri river station protecting refinery & Kaziranga buffer zones."
    },
    {
        "id": "AS-JIA-01", "name": "Tezpur", "river": "Jia Bharali River", "region": "Assam",
        "requested_lat": 26.5833, "requested_lon": 92.5500, "elevation_m": 68.0,
        "warning_level_m": 64.0, "danger_level_m": 65.5, "normal_level_m": 60.0,
        "description": "Sonitpur district Jia Bharali confluence node monitoring North Bank Himalayan runoff."
    }
]

PROXIES_CACHE = []

def load_proxies():
    global PROXIES_CACHE
    if not PROXIES_CACHE:
        try:
            url_list = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
            resp = requests.get(url_list, verify=False, timeout=5)
            PROXIES_CACHE = [p.strip() for p in resp.text.split('\n') if p.strip()][:200]
        except Exception:
            PROXIES_CACHE = []
    return PROXIES_CACHE

def safe_get_json(url: str, max_retries: int = 5) -> dict:
    """Fetches JSON with proxy fallback for flood-api or direct for archive-api."""
    if "archive-api.open-meteo.com" in url:
        for _ in range(3):
            try:
                resp = requests.get(url, timeout=10.0)
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                time.sleep(1.0)
        return {}

    # Try direct first
    try:
        resp = requests.get(url, timeout=8.0)
        if resp.status_code == 200:
            data = resp.json()
            if not data.get("error"):
                return data
    except Exception:
        pass

    # Try proxies
    proxies = load_proxies()
    if proxies:
        chosen = random.sample(proxies, min(20, len(proxies)))
        for p in chosen:
            try:
                resp = requests.get(url, proxies={'http': f'http://{p}', 'https': f'http://{p}'}, verify=False, timeout=4.0)
                if resp.status_code == 200:
                    data = resp.json()
                    if not data.get("error"):
                        return data
            except Exception:
                pass
                
    time.sleep(1.0)
    raise RuntimeError(f"Failed to fetch from Open-Meteo API: {url}")

def fetch_open_meteo_history(st_id: str, lat: float, lon: float, force_refetch: bool = False) -> Tuple[pd.DataFrame, float, float]:
    """Fetches daily river discharge & precipitation from Open-Meteo for 1990-2024."""
    csv_filename = f"{st_id}_1990_2025.csv"
    csv_path = os.path.join(RAW_DIR, csv_filename)

    if not force_refetch and os.path.exists(csv_path):
        print(f"  [Cache Hit] Loading {csv_filename} from local disk...", flush=True)
        df = pd.read_csv(csv_path)
        df["date"] = pd.to_datetime(df["date"])
        grid_lat, grid_lon = lat, lon
        return df, grid_lat, grid_lon

    url = f"https://flood-api.open-meteo.com/v1/flood?latitude={lat}&longitude={lon}&daily=river_discharge&start_date=1990-01-01&end_date=2024-12-31"
    w_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&daily=precipitation_sum&start_date=1990-01-01&end_date=2024-12-31"

    print(f"  Fetching flood API discharge...", flush=True)
    resp = safe_get_json(url)
    print(f"  Fetching weather archive precipitation...", flush=True)
    w_resp = safe_get_json(w_url)

    grid_lat = float(resp.get("latitude", lat))
    grid_lon = float(resp.get("longitude", lon))

    dates = resp.get("daily", {}).get("time", [])
    discharges = resp.get("daily", {}).get("river_discharge", [])
    
    w_dates = w_resp.get("daily", {}).get("time", [])
    precips = w_resp.get("daily", {}).get("precipitation_sum", [])

    df_f = pd.DataFrame({"date": pd.to_datetime(dates), "river_discharge_m3s": discharges})
    df_w = pd.DataFrame({"date": pd.to_datetime(w_dates), "precipitation_sum_mm": precips})
    df = pd.merge(df_f, df_w, on="date", how="left")
    df["precipitation_sum_mm"] = df["precipitation_sum_mm"].fillna(0.0)
    df["river_discharge_m3s"] = df["river_discharge_m3s"].fillna(0.0)
    return df, grid_lat, grid_lon

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()[:8]

def main():
    print("=" * 120, flush=True)
    print("REBUILDING ROUND 6B HYDROLOGICAL DATASET & THRESHOLDS FROM OPEN-METEO API", flush=True)
    print("=" * 120, flush=True)

    thresholds_dict = {}
    kerala_dfs = []
    assam_dfs = []

    for st in STATIONS_CONFIG:
        st_id = st["id"]
        req_lat = st["requested_lat"]
        req_lon = st["requested_lon"]
        print(f"\nProcessing {st_id} ({st['name']}) at ({req_lat}, {req_lon})...", flush=True)

        force_fetch = (st_id in ["AS-BRA-01", "AS-BRA-02", "AS-JIA-01"])
        df, grid_lat, grid_lon = fetch_open_meteo_history(st_id, req_lat, req_lon, force_refetch=force_fetch)
        df["station_id"] = st_id

        csv_filename = f"{st_id}_1990_2025.csv"
        csv_path = os.path.join(RAW_DIR, csv_filename)
        df.to_csv(csv_path, index=False)
        sha = compute_sha256(csv_path)

        if st["region"] == "Kerala":
            kerala_dfs.append(df)
        else:
            assam_dfs.append(df)

        # Compute 1990-2017 training percentiles & stats
        df["date"] = pd.to_datetime(df["date"])
        df_train = df[(df["date"].dt.year >= 1990) & (df["date"].dt.year <= 2017)].copy()
        q_train = df_train["river_discharge_m3s"].dropna().values

        if len(q_train) == 0:
            q_train = df["river_discharge_m3s"].dropna().values

        q_min = float(np.min(q_train))
        q_med = float(np.median(q_train))
        q_p90 = float(np.percentile(q_train, 90.0))
        q_p97 = float(np.percentile(q_train, 97.0))
        q_p99_5 = float(np.percentile(q_train, 99.5))
        q_max = float(np.max(q_train))

        # 2018 peak
        df_2018 = df[df["date"].dt.year == 2018]
        q_2018_peak = float(np.max(df_2018["river_discharge_m3s"].dropna().values)) if not df_2018.empty else q_max

        # Current live fetch for verification
        live_q = q_med
        try:
            live_url = f"https://flood-api.open-meteo.com/v1/flood?latitude={req_lat}&longitude={req_lon}&daily=river_discharge&past_days=1&forecast_days=1"
            live_resp = safe_get_json(live_url)
            live_q = float(live_resp.get("daily", {}).get("river_discharge", [q_med])[-1])
        except Exception:
            pass

        # Percentile rank of live_q in training distribution
        rank = float(np.mean(q_train <= live_q) * 100.0)

        # Computed risk class
        if live_q >= q_p99_5:
            cls = "Red"
        elif live_q >= q_p97:
            cls = "Orange"
        elif live_q >= q_p90:
            cls = "Yellow"
        else:
            cls = "Green"

        thresholds_dict[st_id] = {
            "name": st["name"],
            "river": st["river"],
            "region": st["region"],
            "requested_lat": req_lat,
            "requested_lon": req_lon,
            "grid_cell_lat": grid_lat,
            "grid_cell_lon": grid_lon,
            "csv_sha256": sha,
            "training_rows": len(q_train),
            "p90_yellow": round(q_p90, 2),
            "p97_orange": round(q_p97, 2),
            "p99.5_red": round(q_p99_5, 2),
            "p99_5_red": round(q_p99_5, 2),
            "historical_min_m3s": round(q_min, 1),
            "historical_median_m3s": round(q_med, 1),
            "historical_max_m3s": round(q_max, 1),
            "peak_2018_m3s": round(q_2018_peak, 1),
            "current_live_m3s": round(live_q, 1),
            "percentile_rank": round(rank, 1),
            "computed_class": cls
        }
        print(f"  --> {st_id} Stats: Median={q_med:.1f}, p90={q_p90:.1f}, p97={q_p97:.1f}, p99.5={q_p99_5:.1f}, Max={q_max:.1f}", flush=True)

    # Save regional combined CSVs
    if kerala_dfs:
        pd.concat(kerala_dfs, ignore_index=True).to_csv(os.path.join(RAW_DIR, "kerala_daily_1990_2025.csv"), index=False)
    if assam_dfs:
        pd.concat(assam_dfs, ignore_index=True).to_csv(os.path.join(RAW_DIR, "assam_daily_1990_2025.csv"), index=False)

    # Save thresholds.json single source of truth
    t_path1 = os.path.abspath(os.path.join(DATA_DIR, "thresholds.json"))
    t_path2 = os.path.abspath(os.path.join(DATA_DIR, "..", "frontend", "public", "data", "thresholds.json"))

    print(f"\nWriting thresholds to:\n  1) {t_path1}\n  2) {t_path2}", flush=True)
    with open(t_path1, "w", encoding="utf-8") as f:
        json.dump(thresholds_dict, f, indent=2)
    with open(t_path2, "w", encoding="utf-8") as f:
        json.dump(thresholds_dict, f, indent=2)

    # Save stations_metadata.json
    meta_list = []
    for st in STATIONS_CONFIG:
        st_id = st["id"]
        meta_list.append({
            "id": st_id,
            "name": st["name"],
            "region": st["region"],
            "river": st["river"],
            "latitude": st["requested_lat"],
            "longitude": st["requested_lon"],
            "elevation_m": st["elevation_m"],
            "warning_level_m": st["warning_level_m"],
            "danger_level_m": st["danger_level_m"],
            "normal_level_m": st["normal_level_m"],
            "description": st["description"],
            "grid_cell_lat": thresholds_dict[st_id]["grid_cell_lat"],
            "grid_cell_lon": thresholds_dict[st_id]["grid_cell_lon"]
        })

    m_path = os.path.join(DATA_DIR, "stations_metadata.json")
    with open(m_path, "w", encoding="utf-8") as f:
        json.dump(meta_list, f, indent=2)

    print("\n[Rebuild Complete] Successfully updated dataset, thresholds.json, and metadata!", flush=True)

if __name__ == "__main__":
    main()
