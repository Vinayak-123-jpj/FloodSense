"""Generates Day-by-Day Historical Disaster Replay Datasets for Kerala 2018 & Assam 2018.

Extracts real observed GloFAS discharge and rainfall, applies station percentile thresholds,
computes rating curve stage, generates plain-language driver summaries from real features,
and writes structured frame-by-frame JSON files to /data and /frontend/public/data.
"""

import os
import json
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FRONTEND_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "data")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FRONTEND_DATA_DIR, exist_ok=True)

# Station percentile thresholds (exact historical training period 1990-2017 m³/s percentiles)
STATION_PERCENTILES = {
    "KL-PER-01": {"p90_yellow": 4.3,     "p97_orange": 5.9,     "p99.5_red": 7.9,     "a": 12.0, "b": 2.1, "h0": 1.2},
    "KL-PER-02": {"p90_yellow": 437.5,   "p97_orange": 600.2,   "p99.5_red": 809.7,   "a": 14.0, "b": 2.2, "h0": 1.0},
    "KL-PAM-01": {"p90_yellow": 167.7,   "p97_orange": 233.4,   "p99.5_red": 325.5,   "a": 10.0, "b": 2.0, "h0": 1.5},
    "KL-ACH-01": {"p90_yellow": 41.7,    "p97_orange": 60.2,    "p99.5_red": 87.9,    "a": 8.0,  "b": 2.0, "h0": 1.3},
    "KL-CHA-01": {"p90_yellow": 156.4,   "p97_orange": 221.4,   "p99.5_red": 290.7,   "a": 11.0, "b": 2.1, "h0": 1.2},
    "KL-MUV-01": {"p90_yellow": 41.8,    "p97_orange": 59.7,    "p99.5_red": 84.5,    "a": 9.0,  "b": 2.0, "h0": 1.1},
    "AS-BRA-01": {"p90_yellow": 20.0,    "p97_orange": 31.4,    "p99.5_red": 52.1,    "a": 50.0, "b": 2.3, "h0": 40.0},
    "AS-BRA-02": {"p90_yellow": 3.4,     "p97_orange": 5.0,     "p99.5_red": 8.2,     "a": 55.0, "b": 2.3, "h0": 95.0},
    "AS-KOP-01": {"p90_yellow": 693.1,   "p97_orange": 1155.1,  "p99.5_red": 1938.7,  "a": 10.0, "b": 2.0, "h0": 52.0},
    "AS-DHA-01": {"p90_yellow": 800.7,   "p97_orange": 1118.4,  "p99.5_red": 1671.4,  "a": 11.0, "b": 2.0, "h0": 70.0},
    "AS-JIA-01": {"p90_yellow": 27063.5, "p97_orange": 36811.9,  "p99.5_red": 45261.7, "a": 10.0, "b": 2.0, "h0": 70.0}
}

STATION_INFO = {
    "KL-PER-01": {"name": "Neeleswaram", "river": "Periyar River", "lat": 10.1416, "lng": 76.5781},
    "KL-PER-02": {"name": "Aluva", "river": "Periyar River", "lat": 10.1076, "lng": 76.3516},
    "KL-PAM-01": {"name": "Chengannur", "river": "Pamba River", "lat": 9.3175, "lng": 76.6122},
    "KL-ACH-01": {"name": "Thumpamon", "river": "Achenkovil River", "lat": 9.2560, "lng": 76.7110},
    "KL-CHA-01": {"name": "Chalakudy", "river": "Chalakudy River", "lat": 10.3070, "lng": 76.3323},
    "KL-MUV-01": {"name": "Muvattupuzha", "river": "Muvattupuzha River", "lat": 9.9813, "lng": 76.5772},
    "AS-BRA-01": {"name": "Guwahati", "river": "Brahmaputra River", "lat": 26.1833, "lng": 91.7500},
    "AS-BRA-02": {"name": "Dibrugarh", "river": "Brahmaputra River", "lat": 27.4728, "lng": 94.9120},
    "AS-KOP-01": {"name": "Kampur", "river": "Kopili River", "lat": 26.1500, "lng": 92.5833},
    "AS-DHA-01": {"name": "Numaligarh", "river": "Dhansiri River", "lat": 26.5667, "lng": 93.7333},
    "AS-JIA-01": {"name": "Tezpur", "river": "Jia Bharali River", "lat": 26.6333, "lng": 92.8000}
}

def discharge_to_stage(q: float, params: dict) -> float:
    """Converts river discharge (m³/s) to water level stage (m) via inverted rating curve."""
    a, b, h0 = params["a"], params["b"], params["h0"]
    if q <= 0:
        return h0
    try:
        stage = h0 + (q / a) ** (1.0 / b)
        return round(float(stage), 2)
    except Exception:
        return round(h0 + 0.5, 2)

def evaluate_risk(q: float, p: dict) -> str:
    """Assigns risk level against station's percentile proxies."""
    if q >= p["p99.5_red"]:
        return "Red"
    elif q >= p["p97_orange"]:
        return "Orange"
    elif q >= p["p90_yellow"]:
        return "Yellow"
    return "Green"

def build_kerala_2018_replay():
    csv_path = os.path.join(DATA_DIR, "raw", "kerala_daily_1990_2025.csv")
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"].astype(str).str[:10])
    aug = df[(df["date"] >= "2018-08-01") & (df["date"] <= "2018-08-31")].copy()

    # Precompute rolling 7d rain for drivers
    kerala_full = df[df["date"] <= "2018-08-31"].copy()
    kerala_full = kerala_full.sort_values(["station_id", "date"]).reset_index(drop=True)
    kerala_full["rain_7d"] = kerala_full.groupby("station_id")["precipitation_sum_mm"].rolling(7, min_periods=1).sum().reset_index(drop=True)

    aug_merged = pd.merge(
        aug,
        kerala_full[["station_id", "date", "rain_7d"]],
        on=["station_id", "date"],
        how="left"
    )

    dates = sorted(aug_merged["date"].unique())
    frames = []

    for idx, d in enumerate(dates):
        d_str = str(d)[:10]
        day_df = aug_merged[aug_merged["date"] == d]
        progress_pct = round((idx / max(1, len(dates) - 1)) * 100.0, 1)

        station_records = []
        overall_risk_prio = {"Green": 0, "Yellow": 1, "Orange": 2, "Red": 3}
        max_prio = 0
        current_overall_risk = "Green"

        for _, row in day_df.iterrows():
            st_id = row["station_id"]
            if st_id not in STATION_PERCENTILES:
                continue

            q = float(row["river_discharge_m3s"])
            rain = float(row["precipitation_sum_mm"])
            rain_7d = float(row.get("rain_7d", rain * 3.0))

            p_params = STATION_PERCENTILES[st_id]
            st_info = STATION_INFO.get(st_id, {"name": st_id, "river": "River", "lat": 10.0, "lng": 76.0})

            # During peak days (Aug 14-20), Aluva, Chalakudy, Chengannur carry massive flood discharge
            risk = evaluate_risk(q, p_params)
            prio = overall_risk_prio.get(risk, 0)
            if prio > max_prio:
                max_prio = prio
                current_overall_risk = risk

            stage_m = discharge_to_stage(q, p_params)

            # Plain-language top drivers using ONLY real features
            top_drivers = [
                f"River discharge ({q:.1f} m³/s) vs p97 Warning proxy ({p_params['p97_orange']:.1f} m³/s)",
                f"1-day rainfall ({rain:.1f} mm)",
                f"7-day cumulative rainfall ({rain_7d:.1f} mm)"
            ]

            station_records.append({
                "id": st_id,
                "name": st_info["name"],
                "river": st_info["river"],
                "latitude": st_info["lat"],
                "longitude": st_info["lng"],
                "discharge_m3s": round(q, 1),
                "water_level_m": stage_m,
                "rainfall_mm": round(rain, 1),
                "rain_7d_mm": round(rain_7d, 1),
                "risk_level": risk,
                "percentiles": {
                    "p90_yellow": p_params["p90_yellow"],
                    "p97_orange": p_params["p97_orange"],
                    "p99.5_red": p_params["p99.5_red"]
                },
                "top_drivers": top_drivers
            })

        # Headline
        if current_overall_risk == "Red":
            headline = f"{d_str}: CATASTROPHIC FLOOD DELUGE — RED ALERT"
        elif current_overall_risk == "Orange":
            headline = f"{d_str}: SEVERE CATCHMENT SATURATION — ORANGE WARNING"
        elif current_overall_risk == "Yellow":
            headline = f"{d_str}: ELEVATED DISCHARGE & MONSOON SPELL — YELLOW WATCH"
        else:
            headline = f"{d_str}: BASELINE HYDROLOGICAL CONDITIONS — GREEN"

        frames.append({
            "day_index": idx + 1,
            "date": d_str,
            "progress_pct": progress_pct,
            "headline": headline,
            "overall_risk": current_overall_risk,
            "stations": station_records
        })

    replay_data = {
        "scenario": "kerala_2018",
        "name": "Kerala August 2018 Flood Deluge Replay",
        "region": "Kerala",
        "start_date": "2018-08-01",
        "end_date": "2018-08-31",
        "total_days": len(frames),
        "frames": frames
    }

    out_backend = os.path.join(DATA_DIR, "replay_kerala_2018.json")
    out_frontend = os.path.join(FRONTEND_DATA_DIR, "replay_kerala_2018.json")

    with open(out_backend, "w", encoding="utf-8") as f:
        json.dump(replay_data, f, indent=2)
    with open(out_frontend, "w", encoding="utf-8") as f:
        json.dump(replay_data, f, indent=2)

    print(f"[Replay Generator] Saved {len(frames)} Kerala 2018 frames to {out_backend} and {out_frontend}")

def build_assam_2020_replay():
    csv_path = os.path.join(DATA_DIR, "raw", "assam_daily_1990_2025.csv")
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"].astype(str).str[:10])
    jul = df[(df["date"] >= "2020-07-01") & (df["date"] <= "2020-07-31")].copy()

    assam_full = df[df["date"] <= "2020-07-31"].copy()
    assam_full = assam_full.sort_values(["station_id", "date"]).reset_index(drop=True)
    assam_full["rain_7d"] = assam_full.groupby("station_id")["precipitation_sum_mm"].rolling(7, min_periods=1).sum().reset_index(drop=True)

    jul_merged = pd.merge(
        jul,
        assam_full[["station_id", "date", "rain_7d"]],
        on=["station_id", "date"],
        how="left"
    )

    dates = sorted(jul_merged["date"].unique())
    frames = []

    for idx, d in enumerate(dates):
        d_str = str(d)[:10]
        day_df = jul_merged[jul_merged["date"] == d]
        progress_pct = round((idx / max(1, len(dates) - 1)) * 100.0, 1)

        station_records = []
        overall_risk_prio = {"Green": 0, "Yellow": 1, "Orange": 2, "Red": 3}
        max_prio = 0
        current_overall_risk = "Green"

        for _, row in day_df.iterrows():
            st_id = row["station_id"]
            if st_id not in STATION_PERCENTILES:
                continue

            q = float(row["river_discharge_m3s"])
            rain = float(row["precipitation_sum_mm"])
            rain_7d = float(row.get("rain_7d", rain * 3.0))

            p_params = STATION_PERCENTILES[st_id]
            st_info = STATION_INFO.get(st_id, {"name": st_id, "river": "River", "lat": 26.0, "lng": 92.0})

            risk = evaluate_risk(q, p_params)
            prio = overall_risk_prio.get(risk, 0)
            if prio > max_prio:
                max_prio = prio
                current_overall_risk = risk

            stage_m = discharge_to_stage(q, p_params)

            top_drivers = [
                f"River discharge ({q:.1f} m³/s) vs p97 Warning proxy ({p_params['p97_orange']:.1f} m³/s)",
                f"1-day rainfall ({rain:.1f} mm)",
                f"7-day cumulative rainfall ({rain_7d:.1f} mm)"
            ]

            station_records.append({
                "id": st_id,
                "name": st_info["name"],
                "river": st_info["river"],
                "latitude": st_info["lat"],
                "longitude": st_info["lng"],
                "discharge_m3s": round(q, 1),
                "water_level_m": stage_m,
                "rainfall_mm": round(rain, 1),
                "rain_7d_mm": round(rain_7d, 1),
                "risk_level": risk,
                "percentiles": {
                    "p90_yellow": p_params["p90_yellow"],
                    "p97_orange": p_params["p97_orange"],
                    "p99.5_red": p_params["p99.5_red"]
                },
                "top_drivers": top_drivers
            })

        if current_overall_risk == "Red":
            headline = f"{d_str}: CATASTROPHIC BRAHMAPUTRA DELUGE — RED ALERT"
        elif current_overall_risk == "Orange":
            headline = f"{d_str}: SEVERE RIVER OVERFLOW — ORANGE WARNING"
        elif current_overall_risk == "Yellow":
            headline = f"{d_str}: HIGH MONSOON DISCHARGE — YELLOW WATCH"
        else:
            headline = f"{d_str}: MONSOON SEASON BASELINE — GREEN"

        frames.append({
            "day_index": idx + 1,
            "date": d_str,
            "progress_pct": progress_pct,
            "headline": headline,
            "overall_risk": current_overall_risk,
            "stations": station_records
        })

    replay_data = {
        "scenario": "assam_2020",
        "name": "Assam July 2020 Monsoon Floods Replay",
        "region": "Assam",
        "start_date": "2020-07-01",
        "end_date": "2020-07-31",
        "total_days": len(frames),
        "frames": frames
    }

    out_backend = os.path.join(DATA_DIR, "replay_assam_2020.json")
    out_frontend = os.path.join(FRONTEND_DATA_DIR, "replay_assam_2020.json")

    with open(out_backend, "w", encoding="utf-8") as f:
        json.dump(replay_data, f, indent=2)
    with open(out_frontend, "w", encoding="utf-8") as f:
        json.dump(replay_data, f, indent=2)

    print(f"[Replay Generator] Saved {len(frames)} Assam 2020 frames to {out_backend} and {out_frontend}")

if __name__ == "__main__":
    build_kerala_2018_replay()
    build_assam_2020_replay()
