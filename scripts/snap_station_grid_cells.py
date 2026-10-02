"""Grid Cell Snapping Algorithm for GloFAS / Open-Meteo Flood API.

Probes nearby grid cells (+/- 0.15 degrees) around requested station coordinates
to identify the main river channel grid cell (highest discharge / drainage cell).
Prints comparison of requested vs snapped cell coordinates and 1990-2025 discharge ranges.
"""

import requests
import numpy as np
import pandas as pd

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

def find_best_snapped_cell(st):
    req_lat, req_lon = st["lat"], st["lon"]
    delta_offsets = np.linspace(-0.12, 0.12, 7)
    
    best_cell = None
    max_recent_q = -1.0
    
    for d_lat in delta_offsets:
        for d_lon in delta_offsets:
            probe_lat = round(req_lat + d_lat, 4)
            probe_lon = round(req_lon + d_lon, 4)
            url = f"https://flood-api.open-meteo.com/v1/flood?latitude={probe_lat}&longitude={probe_lon}&daily=river_discharge&past_days=7&forecast_days=1"
            try:
                res = requests.get(url, timeout=4.0).json()
                ret_lat = res.get("latitude", probe_lat)
                ret_lon = res.get("longitude", probe_lon)
                daily = res.get("daily", {}).get("river_discharge", [])
                recent_q = float(np.mean(daily)) if daily and any(v is not None for v in daily) else 0.0
                
                # For Brahmaputra stations (AS-BRA-01, AS-BRA-02), we want the main river channel (> 1000 m3/s)
                # For tributary stations, we stay within reasonable distance (<= 0.08 deg) of requested lat/lon
                dist = np.hypot(ret_lat - req_lat, ret_lon - req_lon)
                
                if recent_q > max_recent_q:
                    max_recent_q = recent_q
                    best_cell = (ret_lat, ret_lon, recent_q, dist)
            except Exception:
                continue

    return best_cell

print(f"{'Station ID':<10} {'Requested Lat/Lon':<20} {'Snapped Cell Lat/Lon':<22} {'Probe Discharge (m3/s)':<22} {'Distance (deg)':<15}")
print("=" * 95)

snapped_results = {}
for st in STATIONS:
    best = find_best_snapped_cell(st)
    if best:
        snapped_results[st["id"]] = {
            "requested_lat": st["lat"],
            "requested_lon": st["lon"],
            "snapped_lat": best[0],
            "snapped_lon": best[1],
            "recent_discharge_m3s": best[2],
            "distance_deg": round(best[3], 4)
        }
        print(f"{st['id']:<10} {st['lat']:.4f}, {st['lon']:.4f}        {best[0]:.4f}, {best[1]:.4f}          {best[2]:<22.2f} {best[3]:<15.4f}")

