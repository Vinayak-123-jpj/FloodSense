"""Probe Open-Meteo Flood API grid around Brahmaputra stations to locate mainstem river cells.

Probes a 0.5° x 0.5° grid (±0.25° in 0.05° steps) for:
1. Guwahati (AS-BRA-01)
2. Dibrugarh (AS-BRA-02)
3. Tezpur (AS-JIA-01)

Finds the cell with the maximum long-term mean discharge (Brahmaputra mainstem).
"""

import requests
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

STATIONS = {
    "AS-BRA-01": {"name": "Guwahati", "lat": 26.1833, "lon": 91.7500},
    "AS-BRA-02": {"name": "Dibrugarh", "lat": 27.4728, "lon": 94.9120},
    "AS-JIA-01": {"name": "Tezpur", "lat": 26.6333, "lon": 92.8000},
    "AS-DHA-01": {"name": "Numaligarh", "lat": 26.5667, "lon": 93.7333},
}

def probe_grid(st_id: str, base_lat: float, base_lon: float) -> List[Dict]:
    results = []
    lat_steps = np.arange(-0.25, 0.26, 0.05)
    lon_steps = np.arange(-0.25, 0.26, 0.05)

    seen_cells = set()

    for d_lat in lat_steps:
        for d_lon in lon_steps:
            target_lat = round(base_lat + d_lat, 4)
            target_lon = round(base_lon + d_lon, 4)

            url = f"https://flood-api.open-meteo.com/v1/flood?latitude={target_lat}&longitude={target_lon}&daily=river_discharge&start_date=2015-01-01&end_date=2024-12-31"
            try:
                resp = requests.get(url, timeout=5.0)
                if resp.status_code != 200:
                    continue
                body = resp.json()
                grid_lat = round(body.get("latitude", target_lat), 4)
                grid_lon = round(body.get("longitude", target_lon), 4)
                
                cell_key = (grid_lat, grid_lon)
                if cell_key in seen_cells:
                    continue
                seen_cells.add(cell_key)

                q_series = body.get("daily", {}).get("river_discharge", [])
                q_clean = [q for q in q_series if q is not None]
                if not q_clean:
                    continue

                q_mean = float(np.mean(q_clean))
                q_median = float(np.median(q_clean))
                q_max = float(np.max(q_clean))

                results.append({
                    "station_id": st_id,
                    "target_lat": target_lat,
                    "target_lon": target_lon,
                    "grid_lat": grid_lat,
                    "grid_lon": grid_lon,
                    "mean_m3s": round(q_mean, 1),
                    "median_m3s": round(q_median, 1),
                    "max_m3s": round(q_max, 1)
                })
            except Exception as e:
                pass

    results.sort(key=lambda x: x["mean_m3s"], reverse=True)
    return results

if __name__ == "__main__":
    best_mainstem_cells = {}

    for st_id in ["AS-BRA-01", "AS-BRA-02", "AS-JIA-01"]:
        info = STATIONS[st_id]
        print("=" * 100)
        print(f"PROBING GRID FOR {st_id} ({info['name']}) AT ({info['lat']}, {info['lon']}) ±0.25°")
        print("=" * 100)
        
        probe_results = probe_grid(st_id, info["lat"], info["lon"])
        
        print(f"{'Rank':<5} {'Req Lat/Lon':<18} {'Grid Cell Lat/Lon':<20} {'Mean Q (m³/s)':<15} {'Median Q (m³/s)':<16} {'Max Q (m³/s)':<15}")
        print("-" * 100)
        
        for idx, row in enumerate(probe_results[:10], 1):
            req_str = f"{row['target_lat']:.4f},{row['target_lon']:.4f}"
            cell_str = f"{row['grid_lat']:.4f},{row['grid_lon']:.4f}"
            print(f"{idx:<5} {req_str:<18} {cell_str:<20} {row['mean_m3s']:<15.1f} {row['median_m3s']:<16.1f} {row['max_m3s']:<15.1f}")
        
        if probe_results:
            best = probe_results[0]
            best_mainstem_cells[st_id] = best
            print(f"\n---> CHOSEN MAINSTEM CELL FOR {st_id} ({info['name']}): Grid ({best['grid_lat']}, {best['grid_lon']}) with Mean Q = {best['mean_m3s']} m³/s, Median Q = {best['median_m3s']} m³/s, Max Q = {best['max_m3s']} m³/s\n")

    # Downstream ordering check
    print("=" * 100)
    print("BRAHMAPUTRA RIVER MAINSTEM DOWNSTREAM ORDERING CHECK")
    print("=" * 100)
    print("Expected Downstream Order: Dibrugarh (Upstream) -> Numaligarh (Tributary/Mainstem) -> Tezpur (Midstream) -> Guwahati (Downstream)")
    print("-" * 100)
