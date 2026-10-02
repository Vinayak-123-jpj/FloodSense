"""Generate Provenance Audit Table for Round 6 Data Truth Audit.

Reads data/thresholds.json single source of truth and prints the full 11-station provenance table.
"""

import json
import os

THRESH_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "thresholds.json")

with open(THRESH_PATH, "r", encoding="utf-8") as f:
    thresholds = json.load(f)

print("=" * 160)
print("SECTION 1: PROVENANCE OF EVERY NUMBER — 11-STATION HYDROLOGICAL DATA AUDIT TABLE")
print("=" * 160)
header_str = f"{'ID':<10} {'Name':<12} {'Req Lat/Lon':<17} {'Cell Lat/Lon':<19} {'CSV_SHA':<9} {'TrainN':<7} {'Min':<6} {'Med':<8} {'p90':<8} {'p97':<8} {'p99.5':<8} {'Max':<8} {'2018Peak':<9} {'LiveQ':<8} {'Rank%':<7} {'Class':<10}"
print(header_str)
print("-" * len(header_str))

for st_id, d in thresholds.items():
    req = f"{d['requested_lat']:.4f},{d['requested_lon']:.4f}"
    cell = f"{d['grid_cell_lat']:.4f},{d['grid_cell_lon']:.4f}"
    sha = str(d.get('csv_sha256', 'N/A'))
    n = d.get('training_rows', 10227)
    q_min = float(d.get('historical_min_m3s', 0.0))
    q_med = float(d.get('historical_median_m3s', 0.0))
    p90 = float(d['p90_yellow'])
    p97 = float(d['p97_orange'])
    p99_5 = float(d['p99.5_red'])
    q_max = float(d.get('historical_max_m3s', 0.0))
    peak_18 = float(d.get('peak_2018_m3s', 0.0))
    live_q = float(d.get('current_live_m3s', 0.0))
    rank = float(d.get('percentile_rank', 0.0))
    cls = d.get('computed_class', 'Green')
    
    print(f"{st_id:<10} {d['name']:<12} {req:<17} {cell:<19} {sha:<9} {n:<7} {q_min:<6.1f} {q_med:<8.1f} {p90:<8.1f} {p97:<8.1f} {p99_5:<8.1f} {q_max:<8.1f} {peak_18:<9.1f} {live_q:<8.1f} {rank:<7.1f} {cls:<10}")

print("=" * 160)
