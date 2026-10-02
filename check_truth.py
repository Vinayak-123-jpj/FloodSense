import requests, pandas as pd, numpy as np, time, os

# grid cells taken from the agent's own reports
S = {
 "KL-PER-01 Neeleswaram": (10.125, 76.575), "KL-PER-02 Aluva": (10.125, 76.375),
 "KL-PAM-01 Chengannur": (9.325, 76.625),  "KL-MUV-01 Muvattupuzha": (9.975, 76.575),
 "KL-CHA-01 Chalakudy": (10.325, 76.325),  "KL-ACH-01 Thumpamon": (9.275, 76.725),
 "AS-BRA-01 Guwahati": (26.225, 91.775),   "AS-BRA-02 Dibrugarh": (27.425, 94.725),
 "AS-JIA-01 Tezpur": (26.625, 92.825),     "AS-KOP-01 Kampur": (26.175, 92.575),
 "AS-DHA-01 Numaligarh": (26.575, 93.725),
}
os.makedirs("truth_csv", exist_ok=True)

def fetch(lat, lon):
    for _ in range(4):
        try:
            r = requests.get("https://flood-api.open-meteo.com/v1/flood", params=dict(
                latitude=lat, longitude=lon, daily="river_discharge",
                start_date="1990-01-01", end_date="2025-09-30"), timeout=90)
            r.raise_for_status()
            d = r.json()["daily"]
            return pd.Series(d["river_discharge"], index=pd.to_datetime(d["time"])).dropna()
        except Exception as e:
            print("retry", e); time.sleep(5)
    return None

rows = []
for name, (lat, lon) in S.items():
    s = fetch(lat, lon)
    if s is None or s.empty:
        rows.append((name, "NO DATA")); continue
    s.to_csv(f"truth_csv/{name.split()[0]}.csv")
    tr = s[:"2017-12-31"]
    p90, p97, p995 = np.percentile(tr, [90, 97, 99.5])
    y18 = s["2018-01-01":"2018-12-31"]
    rows.append((name, len(tr), round(tr.median(), 1), round(p90, 1), round(p97, 1),
                 round(p995, 1), round(tr.max(), 1), len(y18), int((y18 > p97).sum()), round(y18.max(), 1)))
    time.sleep(1)

print(pd.DataFrame(rows, columns=["station","train_n","median","p90","p97","p99.5","max","n2018","days>p97_2018","peak2018"]).to_string(index=False))