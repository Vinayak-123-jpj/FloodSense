"""Wide Probe for Brahmaputra Mainstem Grid Cells.

Probes Open-Meteo Flood API up to ±0.75° around Guwahati and Dibrugarh
to locate the mainstem Brahmaputra river channel grid cells (discharge > 1000 m³/s).
"""

import requests
import numpy as np
import time

def probe_wide(st_id: str, name: str, center_lat: float, center_lon: float, max_offset: float = 0.6):
    print("=" * 100)
    print(f"WIDE PROBE FOR {st_id} ({name}) CENTERED AT ({center_lat}, {center_lon}) ±{max_offset}°")
    print("=" * 100)

    lats = np.arange(center_lat - max_offset, center_lat + max_offset + 0.01, 0.05)
    lons = np.arange(center_lon - max_offset, center_lon + max_offset + 0.01, 0.05)

    results = []
    seen = set()

    for lat in lats:
        for lon in lons:
            req_lat = round(float(lat), 4)
            req_lon = round(float(lon), 4)
            url = f"https://flood-api.open-meteo.com/v1/flood?latitude={req_lat}&longitude={req_lon}&daily=river_discharge&start_date=2022-01-01&end_date=2024-12-31"
            try:
                resp = requests.get(url, timeout=4.0)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                grid_lat = round(data.get("latitude", req_lat), 4)
                grid_lon = round(data.get("longitude", req_lon), 4)

                cell_key = (grid_lat, grid_lon)
                if cell_key in seen:
                    continue
                seen.add(cell_key)

                discharges = data.get("daily", {}).get("river_discharge", [])
                clean_q = [q for q in discharges if q is not None]
                if not clean_q:
                    continue

                mean_q = float(np.mean(clean_q))
                med_q = float(np.median(clean_q))
                max_q = float(np.max(clean_q))

                results.append({
                    "req_lat": req_lat,
                    "req_lon": req_lon,
                    "grid_lat": grid_lat,
                    "grid_lon": grid_lon,
                    "mean_q": round(mean_q, 1),
                    "med_q": round(med_q, 1),
                    "max_q": round(max_q, 1)
                })
            except Exception:
                pass

    results.sort(key=lambda x: x["mean_q"], reverse=True)

    print(f"{'Rank':<5} {'Req Lat/Lon':<18} {'Grid Cell Lat/Lon':<20} {'Mean Q (m³/s)':<15} {'Median Q (m³/s)':<16} {'Max Q (m³/s)':<15}")
    print("-" * 100)
    for idx, r in enumerate(results[:15], 1):
        req_str = f"{r['req_lat']:.4f},{r['req_lon']:.4f}"
        cell_str = f"{r['grid_lat']:.4f},{r['grid_lon']:.4f}"
        print(f"{idx:<5} {req_str:<18} {cell_str:<20} {r['mean_q']:<15.1f} {r['med_q']:<16.1f} {r['max_q']:<15.1f}")

    if results:
        top = results[0]
        print(f"\n---> TOP MAINSTEM CELL: Grid ({top['grid_lat']}, {top['grid_lon']}) - Mean: {top['mean_q']} m³/s, Median: {top['med_q']} m³/s, Max: {top['max_q']} m³/s\n")
    return results

if __name__ == "__main__":
    # Probe Guwahati
    probe_wide("AS-BRA-01", "Guwahati", 26.1833, 91.7500, max_offset=0.5)
    # Probe Dibrugarh
    probe_wide("AS-BRA-02", "Dibrugarh", 27.4728, 94.9120, max_offset=0.5)
    # Probe Tezpur
    probe_wide("AS-JIA-01", "Tezpur", 26.6333, 92.8000, max_offset=0.5)
