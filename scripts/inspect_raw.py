import pandas as pd
import numpy as np
import os

data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
k_df = pd.read_csv(os.path.join(data_dir, "kerala_daily_1990_2025.csv"))
a_df = pd.read_csv(os.path.join(data_dir, "assam_daily_1990_2025.csv"))

df = pd.concat([k_df, a_df], ignore_index=True)
print(f"Total Combined Rows: {len(df)}")
print("\nPer Station Breakdown:")
for st_id, grp in df.groupby("station_id"):
    grp["year"] = pd.to_datetime(grp["date"]).dt.year
    train_grp = grp[grp["year"] <= 2017]
    q = train_grp["river_discharge_m3s"].dropna().values
    p90 = np.percentile(q, 90)
    p97 = np.percentile(q, 97)
    p99_5 = np.percentile(q, 99.5)
    print(f"{st_id:<10}: Rows={len(grp)} | TrainRows={len(train_grp)} | Min={np.min(q):.2f}, Med={np.median(q):.2f}, Max={np.max(q):.2f} | p90={p90:.2f}, p97={p97:.2f}, p99.5={p99_5:.2f}")
