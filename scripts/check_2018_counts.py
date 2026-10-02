import sys
sys.path.insert(0, ".")
import pandas as pd
import json
from backend.ml.feature_engineering import compute_station_percentiles, build_daily_features

df_k = pd.read_csv('data/raw/kerala_daily_1990_2025.csv')
df_a = pd.read_csv('data/raw/assam_daily_1990_2025.csv')
df_raw = pd.concat([df_k, df_a], ignore_index=True)
df_raw['date'] = pd.to_datetime(df_raw['date'])

# Protocol B 1990-2017 training set
raw_train_b = df_raw[(df_raw['date'] < '2017-12-25') | (df_raw['date'] > '2019-01-07')].copy()
pct_b = compute_station_percentiles(raw_train_b)

df_fe = build_daily_features(df_raw, pct_b, horizon_days=1)
df_2018 = df_fe[(df_fe['date'] >= '2018-01-01') & (df_fe['date'] <= '2018-12-31')]

print(f"{'Station ID':<12} {'p97 (Orange)':<15} {'Orange Days':<12} {'Red Days':<10} {'Actual Orange+Red Days 2018'}")
print('-' * 70)
for st_id, group in df_2018.groupby('station_id'):
    p97 = pct_b[st_id]['p97_orange']
    counts = group['current_risk_at_t'].value_counts().to_dict()
    o = counts.get(2, 0)
    r = counts.get(3, 0)
    print(f"{st_id:<12} {p97:<15.2f} {o:<12} {r:<10} {o+r}")
