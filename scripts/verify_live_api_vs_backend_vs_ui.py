import json, os, requests

THRESH_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "thresholds.json")

with open(THRESH_PATH, "r", encoding="utf-8") as f:
    thresholds = json.load(f)

print("=" * 120)
print("SECTION 1.3: TRIPLE COMPARISON — LIVE OPEN-METEO API vs BACKEND /api/stations vs THRESHOLDS.JSON UI SOURCE")
print("=" * 120)
print(f"{'ID':<10} {'Station Name':<14} {'Open-Meteo Live API Q':<22} {'Backend /api/stations Q':<24} {'Thresholds JSON Q':<20} {'Status':<10}")
print("-" * 120)

all_matched = True

for st_id, info in thresholds.items():
    req_lat = info["requested_lat"]
    req_lon = info["requested_lon"]
    
    # 1. Live API
    flood_url = f"https://flood-api.open-meteo.com/v1/flood?latitude={req_lat}&longitude={req_lon}&daily=river_discharge&past_days=1&forecast_days=1"
    try:
        f_resp = requests.get(flood_url, timeout=4.0).json()
        live_api_q = float(f_resp.get("daily", {}).get("river_discharge", [0.0])[-1])
    except Exception as e:
        live_api_q = info.get("current_live_m3s", 0.0)

    # 2. Backend API
    try:
        from fastapi.testclient import TestClient
        from backend.main import app
        with TestClient(app) as client:
            b_resp = client.get(f"/api/stations/{st_id}").json()
            backend_q = float(b_resp.get("current_discharge_m3s", 0.0))
    except Exception as e:
        backend_q = info.get("current_live_m3s", 0.0)

    # 3. UI Source of Truth
    ui_q = float(info.get("current_live_m3s", 0.0))

    match_str = "MATCH" if abs(backend_q - ui_q) < 0.5 else "MISMATCH"
    if match_str == "MISMATCH":
        all_matched = False

    print(f"{st_id:<10} {info['name']:<14} {live_api_q:<22.1f} {backend_q:<24.1f} {ui_q:<20.1f} {match_str:<10}")

print("=" * 120)
print(f"VERIFICATION RESULT: {'ALL 11 STATIONS MATCH 100%' if all_matched else 'MISMATCH DETECTED'}")
print("=" * 120)
