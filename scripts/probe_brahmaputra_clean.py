import requests
import numpy as np
import json
import time

def probe_grid(name, center_lat, center_lon):
    print(f"\n==================================================================")
    print(f"PROBING GRID FOR {name} CENTERED AT ({center_lat}, {center_lon}) ±0.25°")
    print(f"==================================================================")
    
    # 0.05 step grid within ±0.25
    lats = np.arange(round(center_lat - 0.25, 2), round(center_lat + 0.26, 2), 0.05)
    lons = np.arange(round(center_lon - 0.25, 2), round(center_lon + 0.26, 2), 0.05)
    
    results = {}
    
    for lat in lats:
        for lon in lons:
            req_lat = round(float(lat), 4)
            req_lon = round(float(lon), 4)
            url = f"https://flood-api.open-meteo.com/v1/flood?latitude={req_lat}&longitude={req_lon}&daily=river_discharge&start_date=1990-01-01&end_date=2024-12-31"
            for attempt in range(2):
                try:
                    resp = requests.get(url, timeout=4.0)
                    if resp.status_code == 200:
                        data = resp.json()
                        grid_lat = round(float(data.get("latitude", req_lat)), 4)
                        grid_lon = round(float(data.get("longitude", req_lon)), 4)
                        q_arr = data.get("daily", {}).get("river_discharge", [])
                        clean_q = [float(q) for q in q_arr if q is not None]
                        if clean_q:
                            key = (grid_lat, grid_lon)
                            res = {
                                "req_lat": req_lat,
                                "req_lon": req_lon,
                                "grid_lat": grid_lat,
                                "grid_lon": grid_lon,
                                "mean": round(float(np.mean(clean_q)), 1),
                                "median": round(float(np.median(clean_q)), 1),
                                "max": round(float(np.max(clean_q)), 1)
                            }
                            if key not in results or res["mean"] > results[key]["mean"]:
                                results[key] = res
                        break
                    elif resp.status_code == 429:
                        time.sleep(1.0)
                except Exception:
                    time.sleep(0.5)
                    
    sorted_res = sorted(results.values(), key=lambda x: x["mean"], reverse=True)
    
    print(f"{'Rank':<5} {'Req Lat,Lon':<18} {'Grid Cell Lat,Lon':<20} {'Mean (m³/s)':<12} {'Median':<10} {'Max':<10}")
    print("-" * 80)
    for idx, r in enumerate(sorted_res[:10], 1):
        req_str = f"{r['req_lat']:.4f},{r['req_lon']:.4f}"
        grid_str = f"{r['grid_lat']:.4f},{r['grid_lon']:.4f}"
        print(f"{idx:<5} {req_str:<18} {grid_str:<20} {r['mean']:<12.1f} {r['median']:<10.1f} {r['max']:<10.1f}")
        
    top = sorted_res[0] if sorted_res else None
    if top:
        print(f"\n---> CHOSEN CELL FOR {name}: Grid ({top['grid_lat']}, {top['grid_lon']}) - Mean: {top['mean']} m³/s, Max: {top['max']} m³/s\n")
    return top, sorted_res

def main():
    res = {}
    tables = {}
    
    # 1. Guwahati (AS-BRA-01)
    top_g, table_g = probe_grid("Guwahati (AS-BRA-01)", 26.1833, 91.7500)
    res["AS-BRA-01"] = top_g
    tables["AS-BRA-01"] = table_g
    
    # 2. Dibrugarh (AS-BRA-02)
    top_d, table_d = probe_grid("Dibrugarh (AS-BRA-02)", 27.4728, 94.9120)
    res["AS-BRA-02"] = top_d
    tables["AS-BRA-02"] = table_d
    
    # 3. Tezpur (AS-JIA-01)
    top_t, table_t = probe_grid("Tezpur (AS-JIA-01)", 26.6333, 92.8000)
    res["AS-JIA-01"] = top_t
    tables["AS-JIA-01"] = table_t
    
    # Downstream ordering check
    print("\n" + "=" * 80)
    print("DOWNSTREAM DISCHARGE ORDERING CHECK (BRAHMAPUTRA RIVER)")
    print("=" * 80)
    print(f"{'Station Name':<15} {'Station ID':<12} {'Grid Cell':<20} {'Mean Q (m³/s)':<15} {'Median Q':<12} {'Max Q':<12}")
    print("-" * 80)
    
    # Order: Dibrugarh (Upstream) -> Tezpur (Midstream) -> Guwahati (Downstream)
    # Also include Numaligarh (Dhansiri tributary to Brahmaputra)
    for st_id, name in [("AS-BRA-02", "Dibrugarh"), ("AS-JIA-01", "Tezpur"), ("AS-BRA-01", "Guwahati")]:
        c = res[st_id]
        grid_str = f"{c['grid_lat']:.4f},{c['grid_lon']:.4f}"
        print(f"{name:<15} {st_id:<12} {grid_str:<20} {c['mean']:<15.1f} {c['median']:<12.1f} {c['max']:<12.1f}")
        
    with open("scripts/probe_results.json", "w") as f:
        json.dump({"best": res, "tables": tables}, f, indent=2)

if __name__ == "__main__":
    main()
