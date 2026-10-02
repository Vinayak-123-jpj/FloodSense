"""Round 6D Retrain from Scratch & Audit Script.

Fixed Seed: 42
Single Source of Truth Thresholds: data/thresholds.json
Raw Data Source: data/raw/*.csv
"""

import os
import sys
import glob
import json
import hashlib
import joblib
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
import lightgbm as lgb

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from backend.ml.feature_engineering import build_daily_features, compute_station_percentiles, FEATURE_COLUMNS_DAILY

SEED = 42

RIVER_MAP = {
    "KL-PER-01": "Periyar",
    "KL-PER-02": "Periyar",
    "KL-PAM-01": "Pamba",
    "KL-ACH-01": "Achenkovil",
    "KL-CHA-01": "Chalakudy",
    "KL-MUV-01": "Muvattupuzha",
    "AS-BRA-01": "Brahmaputra",
    "AS-BRA-02": "Brahmaputra",
    "AS-KOP-01": "Kopili",
    "AS-DHA-01": "Dhansiri",
    "AS-JIA-01": "Jia Bharali"
}

OLD_LEAD_TIMES = {
    "KL-PER-01": "3 days (24h x 3)",
    "KL-PER-02": "1 day (24h)",
    "KL-PAM-01": "1 day (24h)",
    "KL-MUV-01": "3 days (24h x 3)",
    "KL-CHA-01": "3 days (24h x 3)",
    "KL-ACH-01": "N/A (Short history)",
    "AS-BRA-01": "3 days (24h x 3)",
    "AS-BRA-02": "3 days (24h x 3)",
    "AS-KOP-01": "2 days (48h)",
    "AS-DHA-01": "3 days (24h x 3)",
    "AS-JIA-01": "3 days (24h x 3)"
}

def get_file_hash_and_size(path: str) -> tuple:
    if not os.path.exists(path):
        return "MISSING", 0
    h = hashlib.sha256()
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest(), size

def array_sha256(arr: np.ndarray) -> str:
    h = hashlib.sha256()
    h.update(np.ascontiguousarray(arr).tobytes())
    return h.hexdigest()[:16]

def evaluate_threshold_baseline(X_test: pd.DataFrame) -> np.ndarray:
    y_pred = []
    for _, row in X_test.iterrows():
        if row["discharge_m3s"] >= 500.0 or row["rain_7d"] >= 200.0:
            y_pred.append(3)
        elif row["discharge_m3s"] >= 250.0 or row["rain_7d"] >= 120.0:
            y_pred.append(2)
        elif row["discharge_m3s"] >= 100.0 or row["rain_7d"] >= 50.0:
            y_pred.append(1)
        else:
            y_pred.append(0)
    return np.array(y_pred)

def compute_block_bootstrap_ci(y_true: np.ndarray, y_pred: np.ndarray, n_bootstraps: int = 1000, block_size: int = 7, random_seed: int = 42) -> dict:
    np.random.seed(random_seed)
    n_samples = len(y_true)
    n_blocks = max(1, n_samples // block_size)
    macro_f1s = []
    recalls = []

    for _ in range(n_bootstraps):
        block_indices = np.random.choice(n_blocks, size=n_blocks, replace=True)
        sample_indices = []
        for idx in block_indices:
            start = idx * block_size
            sample_indices.extend(range(start, min(start + block_size, n_samples)))

        sample_indices = np.array(sample_indices[:n_samples])
        yt_sub = y_true[sample_indices]
        yp_sub = y_pred[sample_indices]

        rep = classification_report(yt_sub, yp_sub, labels=[0, 1, 2, 3], output_dict=True, zero_division=0)
        macro_f1s.append(rep.get("macro avg", {}).get("f1-score", 0.0) * 100.0)

        cm = confusion_matrix(yt_sub, yp_sub, labels=[0, 1, 2, 3])
        fn_high = float(cm[2:, :2].sum())
        tp_high = float(cm[2:, 2:].sum())
        rec = (tp_high / (tp_high + fn_high)) * 100.0 if (tp_high + fn_high) > 0 else 0.0
        recalls.append(rec)

    f1_lower, f1_upper = np.percentile(macro_f1s, [2.5, 97.5])
    rec_lower, rec_upper = np.percentile(recalls, [2.5, 97.5])

    return {
        "macro_f1_ci_95": [round(float(f1_lower), 2), round(float(f1_upper), 2)],
        "orange_red_recall_ci_95": [round(float(rec_lower), 2), round(float(rec_upper), 2)]
    }

def evaluate_model_metrics(y_true: np.ndarray, y_pred: np.ndarray, num_stations: int = 5, duration_years: float = 1.0, compute_ci: bool = True, random_seed: int = 42) -> dict:
    labels_all = [0, 1, 2, 3]
    report = classification_report(y_true, y_pred, labels=labels_all, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=labels_all)

    fp_high = float(cm[:, 2:].sum() - (cm[2, 2] + cm[3, 3]))
    tn_high = float(cm[:2, :2].sum())
    far = (fp_high / (fp_high + tn_high)) * 100.0 if (fp_high + tn_high) > 0 else 0.0

    fn_high = float(cm[2:, :2].sum())
    tp_high = float(cm[2:, 2:].sum())

    orange_red_recall = (tp_high / (tp_high + fn_high)) * 100.0 if (tp_high + fn_high) > 0 else 0.0
    orange_red_precision = (tp_high / (tp_high + fp_high)) * 100.0 if (tp_high + fp_high) > 0 else 0.0
    mer = (fn_high / (tp_high + fn_high)) * 100.0 if (tp_high + fn_high) > 0 else 0.0

    fa_per_station_year = round(fp_high / max(1.0, num_stations * duration_years), 2)

    res = {
        "accuracy_pct": round(float(report.get("accuracy", 0.0) * 100.0), 2),
        "macro_f1_pct": round(float(report.get("macro avg", {}).get("f1-score", 0.0) * 100.0), 2),
        "false_alarm_rate_pct": round(float(far), 2),
        "missed_event_rate_pct": round(float(mer), 2),
        "orange_red_recall_pct": round(float(orange_red_recall), 2),
        "orange_red_precision_pct": round(float(orange_red_precision), 2),
        "false_alarms_per_station_year": fa_per_station_year
    }

    if compute_ci:
        ci_dict = compute_block_bootstrap_ci(y_true, y_pred, n_bootstraps=1000, random_seed=random_seed)
        res.update(ci_dict)

    return res

def main():
    print("=" * 100)
    print(" STEP 5 & STEP 6: RETRAIN FROM SCRATCH & STRICT LEAD-TIME AUDIT (Seed=42)")
    print("=" * 100)

    # 1. Inspect existing files before deletion
    targets_to_delete = [
        os.path.join(PROJECT_ROOT, "models", "heldout_2018_model.joblib"),
        os.path.join(PROJECT_ROOT, "models", "flood_risk_model.joblib"),
        os.path.join(PROJECT_ROOT, "reports", "metrics.json"),
        os.path.join(PROJECT_ROOT, "frontend", "public", "reports", "metrics.json"),
        os.path.join(PROJECT_ROOT, "data", "replay_kerala_2018.json"),
        os.path.join(PROJECT_ROOT, "frontend", "public", "data", "replay_kerala_2018.json")
    ]

    print("\n--- PRE-DELETION ARTIFACT AUDIT ---")
    print(f"{'File Path':<65} {'Size (bytes)':<15} {'SHA256 Hash'}")
    print("-" * 110)
    for path in targets_to_delete:
        rel = os.path.relpath(path, PROJECT_ROOT)
        h, sz = get_file_hash_and_size(path)
        print(f"{rel:<65} {sz:<15} {h[:16] if h != 'MISSING' else 'MISSING'}")

    # Delete targets
    print("\nDeleting existing model joblibs, metrics.json, replay json, and caches...")
    for path in targets_to_delete:
        if os.path.exists(path):
            os.remove(path)

    # 2. Load Raw Data & Single Source of Truth Thresholds
    raw_dir = os.path.join(PROJECT_ROOT, "data", "raw")
    thresholds_path = os.path.join(PROJECT_ROOT, "data", "thresholds.json")
    with open(thresholds_path, "r", encoding="utf-8") as f:
        thresholds = json.load(f)

    st_percentiles = {}
    for st_id, info in thresholds.items():
        st_percentiles[st_id] = {
            "p90_yellow": float(info["p90_yellow"]),
            "p97_orange": float(info["p97_orange"]),
            "p99.5_red": float(info["p99.5_red"])
        }

    dfs = []
    for csv_file in glob.glob(os.path.join(raw_dir, "*.csv")):
        df_sub = pd.read_csv(csv_file)
        dfs.append(df_sub)
    
    df_raw = pd.concat(dfs, ignore_index=True)
    df_raw["date"] = pd.to_datetime(df_raw["date"])
    df_raw = df_raw.sort_values(["station_id", "date"]).drop_duplicates(subset=["station_id", "date"]).reset_index(drop=True)

    print(f"\nLoaded {len(df_raw)} raw daily rows across {df_raw['station_id'].nunique()} stations.")

    # 3. Feature Engineering
    df_fe_1d = build_daily_features(df_raw, st_percentiles, horizon_days=1)

    # Filter Kerala 5-station evaluation set (held-out 2018)
    kerala_5st = ["KL-PER-01", "KL-PER-02", "KL-PAM-01", "KL-MUV-01", "KL-CHA-01"]
    
    test_2018_kerala = df_fe_1d[
        (df_fe_1d["date"] >= "2018-01-01") & 
        (df_fe_1d["date"] <= "2018-12-31") & 
        (df_fe_1d["station_id"].isin(kerala_5st))
    ].copy()

    # Training set: 1990-2017 (excluding 2018 +/- 7 days, so date < 2017-12-25 or date > 2019-01-07)
    train_kerala_only = df_fe_1d[
        ((df_fe_1d["date"] < "2017-12-25") | (df_fe_1d["date"] > "2019-01-07")) &
        (df_fe_1d["station_id"].isin(kerala_5st))
    ]

    train_pooled_10st = df_fe_1d[
        ((df_fe_1d["date"] < "2017-12-25") | (df_fe_1d["date"] > "2019-01-07")) &
        (df_fe_1d["station_id"] != "KL-ACH-01")
    ]

    # Fit Kerala-Only model (Primary)
    lgb_kerala = lgb.LGBMClassifier(n_estimators=100, learning_rate=0.05, max_depth=5, class_weight="balanced", random_state=SEED, verbose=-1)
    lgb_kerala.fit(train_kerala_only[FEATURE_COLUMNS_DAILY], train_kerala_only["target_risk_1d"])
    y_pred_kerala = lgb_kerala.predict(test_2018_kerala[FEATURE_COLUMNS_DAILY])

    # Fit Pooled model (Secondary)
    lgb_pooled = lgb.LGBMClassifier(n_estimators=100, learning_rate=0.05, max_depth=5, class_weight="balanced", random_state=SEED, verbose=-1)
    lgb_pooled.fit(train_pooled_10st[FEATURE_COLUMNS_DAILY], train_pooled_10st["target_risk_1d"])
    y_pred_pooled = lgb_pooled.predict(test_2018_kerala[FEATURE_COLUMNS_DAILY])

    # Save trained models
    models_dir = os.path.join(PROJECT_ROOT, "models")
    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(lgb_kerala, os.path.join(models_dir, "heldout_2018_model.joblib"))
    joblib.dump(lgb_pooled, os.path.join(models_dir, "flood_risk_model.joblib"))

    # Compute metrics for 1D Primary vs Secondary
    y_true_kerala = test_2018_kerala["target_risk_1d"].values
    m_kerala = evaluate_model_metrics(y_true_kerala, y_pred_kerala, num_stations=5, duration_years=1.0, random_seed=SEED)
    m_pooled = evaluate_model_metrics(y_true_kerala, y_pred_pooled, num_stations=5, duration_years=1.0, random_seed=SEED)

    hash_kerala = array_sha256(y_pred_kerala)
    hash_pooled = array_sha256(y_pred_pooled)

    print("\n--- HELD-OUT 2018 KERALA MODEL COMPARISON (SEED=42) ---")
    print(f"{'Model Strategy':<25} {'Macro F1 (%) [95% CI]':<26} {'Orange/Red Recall (%) [95% CI]':<32} {'Prediction Array SHA256'}")
    print("-" * 110)
    print(f"{'Kerala-Only (Primary)':<25} {m_kerala['macro_f1_pct']:.2f}% [{m_kerala['macro_f1_ci_95'][0]:.2f}, {m_kerala['macro_f1_ci_95'][1]:.2f}]   {m_kerala['orange_red_recall_pct']:.2f}% [{m_kerala['orange_red_recall_ci_95'][0]:.2f}, {m_kerala['orange_red_recall_ci_95'][1]:.2f}]       {hash_kerala}")
    print(f"{'Pooled 10-Stn (Secondary)':<25} {m_pooled['macro_f1_pct']:.2f}% [{m_pooled['macro_f1_ci_95'][0]:.2f}, {m_pooled['macro_f1_ci_95'][1]:.2f}]   {m_pooled['orange_red_recall_pct']:.2f}% [{m_pooled['orange_red_recall_ci_95'][0]:.2f}, {m_pooled['orange_red_recall_ci_95'][1]:.2f}]       {hash_pooled}")

    # Multi-Horizon Evaluation (D+1, D+2, D+3)
    results_multi_horizon = {}
    for h in [1, 2, 3]:
        df_fe_h = build_daily_features(df_raw, st_percentiles, horizon_days=h)
        train_h = df_fe_h[
            ((df_fe_h["date"] < "2017-12-25") | (df_fe_h["date"] > "2019-01-07")) &
            (df_fe_h["station_id"].isin(kerala_5st))
        ]
        test_h = df_fe_h[
            (df_fe_h["date"] >= "2018-01-01") & 
            (df_fe_h["date"] <= "2018-12-31") &
            (df_fe_h["station_id"].isin(kerala_5st))
        ]

        X_tr, y_tr = train_h[FEATURE_COLUMNS_DAILY], train_h[f"target_risk_{h}d"]
        X_te, y_te = test_h[FEATURE_COLUMNS_DAILY], test_h[f"target_risk_{h}d"]
        y_pers = test_h["current_risk_at_t"].values

        lgb_h = lgb.LGBMClassifier(n_estimators=100, learning_rate=0.05, max_depth=5, class_weight="balanced", random_state=SEED, verbose=-1)
        lgb_h.fit(X_tr, y_tr)
        y_pred_lgb_h = lgb_h.predict(X_te)

        lr_h = LogisticRegression(max_iter=100, class_weight="balanced", random_state=SEED)
        lr_h.fit(X_tr, y_tr)
        y_pred_lr_h = lr_h.predict(X_te)

        y_pred_thresh_h = evaluate_threshold_baseline(X_te)

        results_multi_horizon[f"{h}d"] = {
            "lightgbm": evaluate_model_metrics(y_te.values, y_pred_lgb_h, 5, 1.0, random_seed=SEED),
            "linear_logistic_regression": evaluate_model_metrics(y_te.values, y_pred_lr_h, 5, 1.0, random_seed=SEED),
            "persistence_baseline": evaluate_model_metrics(y_te.values, y_pers, 5, 1.0, random_seed=SEED),
            "threshold_baseline": evaluate_model_metrics(y_te.values, y_pred_thresh_h, 5, 1.0, random_seed=SEED),
            "prediction_sha256": array_sha256(y_pred_lgb_h)
        }

    print("\n--- MULTI-HORIZON HELD-OUT METRICS TABLE (1000 7-day Block Resamples, Seed=42) ---")
    print(f"{'Horizon':<8} {'Model':<25} {'Macro F1 (%) [95% CI]':<26} {'Recall (%) [95% CI]':<26} {'Precision (%)':<15} {'FA / Stn-Yr'}")
    print("-" * 115)
    for h_str, h_dict in results_multi_horizon.items():
        for m_name in ["lightgbm", "persistence_baseline", "threshold_baseline"]:
            m = h_dict[m_name]
            f1_str = f"{m['macro_f1_pct']:.2f}% [{m['macro_f1_ci_95'][0]:.1f}, {m['macro_f1_ci_95'][1]:.1f}]"
            rec_str = f"{m['orange_red_recall_pct']:.2f}% [{m['orange_red_recall_ci_95'][0]:.1f}, {m['orange_red_recall_ci_95'][1]:.1f}]"
            print(f"{h_str:<8} {m_name:<25} {f1_str:<26} {rec_str:<26} {m['orange_red_precision_pct']:<15.2f} {m['false_alarms_per_station_year']}")

    # 4. Strict Lead Time Calculation (Step 6)
    # Event window: 2018-08-01 to 2018-08-31 for Kerala; 2018-07-01 to 2018-08-31 for Assam
    df_fe_1d_all = build_daily_features(df_raw, st_percentiles, horizon_days=1)
    df_2018_all = df_fe_1d_all[(df_fe_1d_all["date"] >= "2018-01-01") & (df_fe_1d_all["date"] <= "2018-12-31")].copy()
    
    # Predict 1D risk using Kerala model for Kerala stations, Pooled for Assam stations
    preds_all = []
    for st_id, grp in df_2018_all.groupby("station_id"):
        if "KL-" in st_id:
            p = lgb_kerala.predict(grp[FEATURE_COLUMNS_DAILY])
        else:
            p = lgb_pooled.predict(grp[FEATURE_COLUMNS_DAILY])
        grp = grp.copy()
        grp["pred_1d"] = p
        preds_all.append(grp)
    
    df_2018_pred = pd.concat(preds_all, ignore_index=True)

    station_2018_stats = {}
    station_lead_times = {}

    print("\n" + "=" * 115)
    print(" STEP 6: STRICT LEAD TIME AUDIT (First warning while prev day observed < Orange vs First observed p97 crossing)")
    print("=" * 115)
    print(f"{'Station ID':<12} {'Station Name':<14} {'First Warning':<15} {'First Crossing':<15} {'Strict Lead Time':<20} {'Git Tag pre-6D Lead'}")
    print("-" * 115)

    all_stations_ordered = [s["id"] for s in json.load(open(os.path.join(PROJECT_ROOT, "data", "stations_metadata.json")))]

    for st_id in all_stations_ordered:
        st_info = thresholds[st_id]
        st_name = st_info["name"]
        p97_thresh = st_percentiles[st_id]["p97_orange"]
        is_short = st_info.get("is_short_history", False)

        if is_short:
            station_lead_times[st_id] = "no event (short history)"
            station_2018_stats[st_id] = {
                "river_name": RIVER_MAP.get(st_id, "Unknown"),
                "event_description": "Excluded (History ends 2009)",
                "actual_orange_red_days_2018": "N/A (Short history)",
                "first_warning_date": "N/A",
                "first_threshold_crossing_date": "N/A",
                "lead_time_display": "no event (short history)",
                "lead_time_days": None
            }
            print(f"{st_id:<12} {st_name:<14} {'N/A':<15} {'N/A':<15} {'no event (short)':<20} {OLD_LEAD_TIMES.get(st_id, 'N/A')}")
            continue

        # Filter event window
        if "KL-" in st_id:
            w_df = df_2018_pred[(df_2018_pred["station_id"] == st_id) & (df_2018_pred["date"] >= "2018-08-01") & (df_2018_pred["date"] <= "2018-08-31")].sort_values("date").reset_index(drop=True)
        else:
            w_df = df_2018_pred[(df_2018_pred["station_id"] == st_id) & (df_2018_pred["date"] >= "2018-07-01") & (df_2018_pred["date"] <= "2018-08-31")].sort_values("date").reset_index(drop=True)

        # 1. First OBSERVED crossing of p97 in window
        cross_rows = w_df[w_df["discharge_m3s"] >= p97_thresh]
        if cross_rows.empty:
            first_cross_date = None
            first_cross_str = "never crossed"
        else:
            first_cross_date = cross_rows.iloc[0]["date"]
            first_cross_str = first_cross_date.strftime("%Y-%m-%d")

        # 2. First MODEL-ISSUED warning (Orange/Red, pred >= 2) while PREVIOUS DAY's observed class was below Orange (observed < p97)
        first_warn_date = None
        first_warn_str = "never warned"
        
        for idx in range(len(w_df)):
            row = w_df.iloc[idx]
            if row["pred_1d"] >= 2: # Orange or Red prediction
                if idx == 0:
                    prev_obs_below_orange = True
                else:
                    prev_obs_discharge = w_df.iloc[idx - 1]["discharge_m3s"]
                    prev_obs_below_orange = (prev_obs_discharge < p97_thresh)
                
                if prev_obs_below_orange:
                    first_warn_date = row["date"]
                    first_warn_str = first_warn_date.strftime("%Y-%m-%d")
                    break

        if first_cross_date is not None and first_warn_date is not None:
            lead_days = (first_cross_date - first_warn_date).days
            if lead_days < 0:
                lead_display = "missed (warned after)"
            elif lead_days >= 3:
                lead_display = ">=3 days (capped)"
            else:
                lead_display = f"{lead_days} day{'s' if lead_days > 1 else ''}"
        elif first_cross_date is None:
            lead_display = "no event"
            lead_days = None
        else:
            lead_display = "missed"
            lead_days = None

        old_lead = OLD_LEAD_TIMES.get(st_id, "N/A")
        station_lead_times[st_id] = lead_display
        
        # Calculate actual 2018 days above p97 threshold
        st_2018_df = df_raw[(df_raw["station_id"] == st_id) & (df_raw["date"] >= "2018-01-01") & (df_raw["date"] <= "2018-12-31")]
        actual_days_2018 = int((st_2018_df["river_discharge_m3s"] >= p97_thresh).sum()) if not is_short else "N/A (Short)"

        station_2018_stats[st_id] = {
            "river_name": RIVER_MAP.get(st_id, "Unknown"),
            "event_description": "August 2018 Kerala Deluge" if "KL-" in st_id else "July-August 2018 Assam Monsoon Flood",
            "actual_orange_red_days_2018": actual_days_2018,
            "first_warning_date": first_warn_str,
            "first_threshold_crossing_date": first_cross_str,
            "strict_lead_time_days": lead_days,
            "lead_time_display": lead_display,
            "git_tag_pre_6d_lead": old_lead
        }

        print(f"{st_id:<12} {st_name:<14} {first_warn_str:<15} {first_cross_str:<15} {lead_display:<20} {old_lead}")

    # 5. Leave-One-River-Out (LORO) Benchmark for Kerala & Assam
    loro_results = {}
    unique_rivers = sorted(list(set(RIVER_MAP.values())))

    for river in unique_rivers:
        held_out_stns = [st for st, r in RIVER_MAP.items() if r == river and st != "KL-ACH-01"]
        train_loro = df_fe_1d[(~df_fe_1d["station_id"].isin(held_out_stns)) & (df_fe_1d["station_id"] != "KL-ACH-01")]
        test_loro = df_fe_1d[df_fe_1d["station_id"].isin(held_out_stns)]

        if test_loro.empty or train_loro.empty:
            continue

        X_tr_l, y_tr_l = train_loro[FEATURE_COLUMNS_DAILY], train_loro["target_risk_1d"]
        X_te_l, y_te_l = test_loro[FEATURE_COLUMNS_DAILY], test_loro["target_risk_1d"]

        lgb_l = lgb.LGBMClassifier(n_estimators=100, class_weight="balanced", random_state=SEED, verbose=-1)
        lgb_l.fit(X_tr_l, y_tr_l)
        y_pred_l = lgb_l.predict(X_te_l)

        loro_results[river] = evaluate_model_metrics(y_te_l.values, y_pred_l, len(held_out_stns), 1.0, compute_ci=False)

    print("\n--- LEAVE-ONE-RIVER-OUT (LORO) SPATIAL GENERALIZATION ---")
    print(f"{'Held-Out River Basin':<20} {'Macro F1 (%)':<15} {'Orange/Red Recall (%)':<22} {'Accuracy (%)':<15}")
    print("-" * 75)
    for river, res in loro_results.items():
        print(f"{river:<20} {res['macro_f1_pct']:<15.2f} {res['orange_red_recall_pct']:<22.2f} {res['accuracy_pct']:<15.2f}")

    # Export metrics.json
    metrics_summary = {
        "dataset_resolution": "DAILY (1 row per station per day)",
        "date_range": "1990-01-01 to 2025-09-30",
        "primary_region": "Kerala (Periyar, Pamba, Muvattupuzha, Chalakudy)",
        "secondary_region": "Assam (Brahmaputra, Dhansiri, Jia Bharali, Kopili)",
        "random_seed": SEED,
        "kerala_only_vs_pooled": {
            "kerala_only_macro_f1": m_kerala["macro_f1_pct"],
            "kerala_only_recall": m_kerala["orange_red_recall_pct"],
            "kerala_only_array_sha256": hash_kerala,
            "pooled_macro_f1": m_pooled["macro_f1_pct"],
            "pooled_recall": m_pooled["orange_red_recall_pct"],
            "pooled_array_sha256": hash_pooled
        },
        "heldout_2018_multi_horizon": results_multi_horizon,
        "leave_one_river_out_loro": loro_results,
        "station_2018_details": station_2018_stats
    }

    rep_path = os.path.join(PROJECT_ROOT, "reports", "metrics.json")
    pub_rep_path = os.path.join(PROJECT_ROOT, "frontend", "public", "reports", "metrics.json")

    with open(rep_path, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)
    with open(pub_rep_path, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)

    print("\n--- POST-TRAINING ARTIFACT AUDIT ---")
    print(f"{'File Path':<65} {'Size (bytes)':<15} {'SHA256 Hash'}")
    print("-" * 110)
    for path in targets_to_delete[:4]:
        rel = os.path.relpath(path, PROJECT_ROOT)
        h, sz = get_file_hash_and_size(path)
        print(f"{rel:<65} {sz:<15} {h[:16]}")

    print(f"\n[Step 5 & Step 6 Complete] Retrain complete with seed {SEED}!")

if __name__ == "__main__":
    main()
