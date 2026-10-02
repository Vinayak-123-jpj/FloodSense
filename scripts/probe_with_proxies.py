"""Brahmaputra Mainstem Grid Probe using Verified HTTP Proxies (2-Stage Fast Probe).

1. Quick-scans 2020-2024 (5 years) to identify mainstem candidate grid cells within ±0.25°.
2. Fetches full 1990-2024 reanalysis for top candidate grid cells to print exact long-term mean and max discharge.
"""

import requests
import numpy as np
import concurrent.futures
import json
import urllib3
import random
import time

urllib3.disable_warnings()

STATIONS = {
    "AS-BRA-01": {"name": "Guwahati", "lat": 26.1833, "lon": 91.7500},
    "AS-BRA-02": {"name": "Dibrugarh", "lat": 27.4728, "lon": 94.9120},
    "AS-JIA-01": {"name": "Tezpur", "lat": 26.6333, "lon": 92.8000}
}

def get_working_proxies():
    print("Fetching proxy list...", flush=True)
    url_list = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
    resp = requests.get(url_list, verify=False, timeout=5)
    all_proxies = [p.strip() for p in resp.text.split('\n') if p.strip()][:300]
    
    test_url = "https://flood-api.open-meteo.com/v1/flood?latitude=26.325&longitude=92.025&daily=river_discharge&start_date=2024-01-01&end_date=2024-01-05"
    working = []
    
    def test_p(p):
        try:
            r = requests.get(test_url, proxies={'http': f'http://{p}', 'https': f'http://{p}'}, verify=False, timeout=2.5).json()
            if 'daily' in r and 'river_discharge' in r['daily']:
                return p
        except Exception:
            pass
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
        futs = [ex.submit(test_p, p) for p in all_proxies]
        for f in concurrent.futures.as_completed(futs):
            val = f.result()
            if val:
                working.append(val)
                
    print(f"Found {len(working)} verified working proxies!", flush=True)
    return working

def fetch_point(args):
    req_lat, req_lon, start_date, end_date, proxies = args
    url = f"https://flood-api.open-meteo.com/v1/flood?latitude={req_lat}&longitude={req_lon}&daily=river_discharge&start_date={start_date}&end_date={end_date}"
    
    chosen_proxies = random.sample(proxies, min(8, len(proxies)))
    for p in chosen_proxies:
        try:
            r = requests.get(url, proxies={'http': f'http://{p}', 'https': f'http://{p}'}, verify=False, timeout=3.5).json()
            if 'daily' in r and 'river_discharge' in r['daily']:
                grid_lat = round(float(r.get("latitude", req_lat)), 4)
                grid_lon = round(float(r.get("longitude", req_lon)), 4)
                discharges = r.get("daily", {}).get("river_discharge", [])
                clean_q = [float(q) for q in discharges if q is not None]
                if clean_q:
                    return {
                        "req_lat": req_lat,
                        "req_lon": req_lon,
                        "grid_lat": grid_lat,
                        "grid_lon": grid_lon,
                        "mean": round(float(np.mean(clean_q)), 1),
                        "median": round(float(np.median(clean_q)), 1),
                        "max": round(float(np.max(clean_q)), 1)
                    }
        except Exception:
            pass
    return None

def probe_station(st_id, info, proxies):
    print(f"\n==================================================================================", flush=True)
    print(f"PROBING {st_id} ({info['name']}) CENTERED AT ({info['lat']}, {info['lon']}) WITHIN ±0.25°", flush=True)
    print(f"==================================================================================", flush=True)
    
    offsets = np.arange(-0.25, 0.251, 0.05)
    points_short = []
    for dlat in offsets:
        for dlon in offsets:
            points_short.append((round(info['lat'] + dlat, 4), round(info['lon'] + dlon, 4), "2020-01-01", "2024-12-31", proxies))
            
    results_map_short = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=35) as ex:
        futs = [ex.submit(fetch_point, p) for p in points_short]
        for f in concurrent.futures.as_completed(futs):
            res = f.result()
            if res:
                key = (res["grid_lat"], res["grid_lon"])
                if key not in results_map_short or res["mean"] > results_map_short[key]["mean"]:
                    results_map_short[key] = res
                    
    sorted_short = sorted(results_map_short.values(), key=lambda x: x["mean"], reverse=True)
    top_candidates = sorted_short[:6]
    
    # Stage 2: Fetch full 1990-2024 for top candidate grid cells
    points_full = [(c["req_lat"], c["req_lon"], "1990-01-01", "2024-12-31", proxies) for c in top_candidates]
    results_map_full = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futs = [ex.submit(fetch_point, p) for p in points_full]
        for f in concurrent.futures.as_completed(futs):
            res = f.result()
            if res:
                key = (res["grid_lat"], res["grid_lon"])
                if key not in results_map_full or res["mean"] > results_map_full[key]["mean"]:
                    results_map_full[key] = res
                    
    sorted_full = sorted(results_map_full.values(), key=lambda x: x["mean"], reverse=True)
    
    print(f"{'Rank':<5} {'Req Lat,Lon':<18} {'Grid Lat,Lon':<18} {'Mean Q (m³/s)':<15} {'Median Q (m³/s)':<15} {'Max Q (m³/s)':<15}", flush=True)
    print("-" * 90, flush=True)
    for idx, r in enumerate(sorted_full, 1):
        req_str = f"{r['req_lat']:.4f}, {r['req_lon']:.4f}"
        grid_str = f"{r['grid_lat']:.4f}, {r['grid_lon']:.4f}"
        print(f"{idx:<5} {req_str:<18} {grid_str:<18} {r['mean']:<15.1f} {r['median']:<15.1f} {r['max']:<15.1f}", flush=True)
        
    top = sorted_full[0] if sorted_full else sorted_short[0]
    print(f"\nSELECTED MAINSTEM CELL FOR {info['name']}: Grid ({top['grid_lat']}, {top['grid_lon']}) | Mean: {top['mean']} m³/s, Median: {top['median']} m³/s, Max: {top['max']} m³/s\n", flush=True)
    return top, sorted_full

def main():
    proxies = get_working_proxies()
    if not proxies:
        print("No working proxies found!", flush=True)
        return
        
    best_cells = {}
    all_tables = {}
    for st_id, info in STATIONS.items():
        top, sorted_res = probe_station(st_id, info, proxies)
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
