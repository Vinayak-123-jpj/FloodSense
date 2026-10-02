"""Ultra Fast Probe for Brahmaputra Grid Cells (within ±0.25°).

1. Quick-scans 2020-2024 to identify mainstem candidate grid cells within ±0.25°.
2. Fetches full 1990-2024 reanalysis for top candidate grid cells to print exact long-term (1990-2024) mean and max discharge.
"""

import requests
import numpy as np
import concurrent.futures
import json
import time

STATIONS = {
    "AS-BRA-01": {"name": "Guwahati", "lat": 26.1833, "lon": 91.7500},
    "AS-BRA-02": {"name": "Dibrugarh", "lat": 27.4728, "lon": 94.9120},
    "AS-JIA-01": {"name": "Tezpur", "lat": 26.6333, "lon": 92.8000}
}

def fetch_probe(args):
    lat, lon, start_date, end_date = args
    url = f"https://flood-api.open-meteo.com/v1/flood?latitude={lat}&longitude={lon}&daily=river_discharge&start_date={start_date}&end_date={end_date}"
    for _ in range(3):
        try:
            resp = requests.get(url, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                grid_lat = round(float(data.get("latitude", lat)), 4)
                grid_lon = round(float(data.get("longitude", lon)), 4)
                discharges = data.get("daily", {}).get("river_discharge", [])
                clean_q = [float(q) for q in discharges if q is not None]
                if clean_q:
                    return {
                        "req_lat": lat,
                        "req_lon": lon,
                        "grid_lat": grid_lat,
                        "grid_lon": grid_lon,
                        "mean": round(float(np.mean(clean_q)), 1),
                        "median": round(float(np.median(clean_q)), 1),
                        "max": round(float(np.max(clean_q)), 1)
                    }
            elif resp.status_code == 429:
                time.sleep(0.5)
        except Exception:
            time.sleep(0.2)
    return None

def probe_station(st_id, info):
    print(f"\n==================================================================================", flush=True)
    print(f"PROBING {st_id} ({info['name']}) CENTERED AT ({info['lat']}, {info['lon']}) WITHIN ±0.25°", flush=True)
    print(f"==================================================================================", flush=True)
    
    offsets = np.arange(-0.25, 0.251, 0.05)
    req_points = []
    for dlat in offsets:
        for dlon in offsets:
            req_points.append((round(info['lat'] + dlat, 4), round(info['lon'] + dlon, 4), "2020-01-01", "2024-12-31"))
            
    results_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(fetch_probe, p) for p in req_points]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res:
                key = (res["grid_lat"], res["grid_lon"])
                if key not in results_map or res["mean"] > results_map[key]["mean"]:
                    results_map[key] = res
                    
    sorted_short = sorted(results_map.values(), key=lambda x: x["mean"], reverse=True)
    top_candidates = sorted_short[:8]
    
    # Re-fetch full 1990-2024 for top candidate cells
    full_points = [(c["req_lat"], c["req_lon"], "1990-01-01", "2024-12-31") for c in top_candidates]
    full_results_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_probe, p) for p in full_points]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res:
                key = (res["grid_lat"], res["grid_lon"])
                if key not in full_results_map or res["mean"] > full_results_map[key]["mean"]:
                    full_results_map[key] = res
                    
    sorted_full = sorted(full_results_map.values(), key=lambda x: x["mean"], reverse=True)
    
    print(f"{'Rank':<5} {'Req Lat,Lon':<18} {'Grid Lat,Lon':<18} {'Mean Q (m³/s)':<15} {'Median Q (m³/s)':<15} {'Max Q (m³/s)':<15}", flush=True)
    print("-" * 90, flush=True)
    for idx, r in enumerate(sorted_full, 1):
        req_str = f"{r['req_lat']:.4f}, {r['req_lon']:.4f}"
        grid_str = f"{r['grid_lat']:.4f}, {r['grid_lon']:.4f}"
        print(f"{idx:<5} {req_str:<18} {grid_str:<18} {r['mean']:<15.1f} {r['median']:<15.1f} {r['max']:<15.1f}", flush=True)
        
    top = sorted_full[0]
    print(f"\nSELECTED MAINSTEM CELL FOR {info['name']}: Grid ({top['grid_lat']}, {top['grid_lon']}) | Mean: {top['mean']} m³/s, Median: {top['median']} m³/s, Max: {top['max']} m³/s\n", flush=True)
    return top, sorted_full

def main():
    best_cells = {}
    all_tables = {}
    for st_id, info in STATIONS.items():
        top, sorted_res = probe_station(st_id, info)
        best_cells[st_id] = top
        all_tables[st_id] = sorted_res
        
    print("\n" + "=" * 90, flush=True)
    print("DOWNSTREAM DISCHARGE ORDERING CHECK ON BRAHMAPUTRA", flush=True)
    print("=" * 90, flush=True)
    
    # Order stations from Upstream to Downstream: Dibrugarh -> Tezpur -> Guwahati
    print(f"{'Station':<15} {'ID':<12} {'Grid Lat,Lon':<20} {'Mean Q (m³/s)':<15} {'Median Q (m³/s)':<15} {'Max Q (m³/s)':<15}", flush=True)
    print("-" * 90, flush=True)
    for st_id in ["AS-BRA-02", "AS-JIA-01", "AS-BRA-01"]:
        cell = best_cells[st_id]
        name = STATIONS[st_id]["name"]
        grid_str = f"{cell['grid_lat']:.4f}, {cell['grid_lon']:.4f}"
        print(f"{name:<15} {st_id:<12} {grid_str:<20} {cell['mean']:<15.1f} {cell['median']:<15.1f} {cell['max']:<15.1f}", flush=True)
        
    with open("scripts/probe_results.json", "w") as f:
        json.dump({"best": best_cells, "tables": all_tables}, f, indent=2)

if __name__ == "__main__":
    main()
