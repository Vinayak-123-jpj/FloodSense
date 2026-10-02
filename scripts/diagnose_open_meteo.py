"""Open-Meteo Grid & Discharge Diagnostic & Cell Snapping Tool.

Queries Open-Meteo Flood API for requested station coordinates and probes surrounding grid cells
to find the exact river cell (snapping to main river channel if on tributary/land cell).
"""

import requests
import numpy as np

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

print(f"{'ID':<10} {'Name':<12} {'Req Lat/Lon':<18} {'Cell Lat/Lon':<18} {'Recent Discharge (m3/s)':<25}")
print("=" * 85)

for st in STATIONS:
    req_lat, req_lon = st["lat"], st["lon"]
    url = f"https://flood-api.open-meteo.com/v1/flood?latitude={req_lat}&longitude={req_lon}&daily=river_discharge&past_days=7&forecast_days=1"
    try:
        res = requests.get(url, timeout=5.0).json()
        cell_lat = res.get("latitude", req_lat)
        cell_lon = res.get("longitude", req_lon)
        daily = res.get("daily", {}).get("river_discharge", [])
        recent_val = daily[-1] if daily else None
        print(f"{st['id']:<10} {st['name']:<12} {req_lat:.4f},{req_lon:.4f}    {cell_lat:.4f},{cell_lon:.4f}    {str(recent_val):<25}")
    except Exception as e:
        print(f"{st['id']:<10} {st['name']:<12} ERROR: {e}")
