# Model Card: FloodSense Multi-Horizon LightGBM Risk Classifier

## Model Details
- **Developer**: FloodSense Team (FOSSEE National Make-A-Thon 2026)
- **Model Date**: October 2026
- **Model Version**: 2.1.0 (Daily Multi-Horizon & 3-Protocol Validation Audit)
- **Model Type**: Multi-class Gradient Boosted Decision Tree (`lightgbm.LGBMClassifier`)
- **License**: MIT License

---

## Intended Use
- **Primary Use**: Predict multi-horizon flood risk levels (Green, Yellow, Orange, Red) for river gauging stations 24h ($t+1\text{d}$), 48h ($t+2\text{d}$), and 72h ($t+3\text{d}$) in advance.
- **Out-of-Scope Use**: Flash flood prediction under 15 minutes or sudden mechanical dam breach warnings.

---

## Technical & Data Science Disclaimers (Data Honesty)
1. **Modeled Discharge**: River discharge ($m^3/s$) is derived from GloFAS reanalysis modeling via Open-Meteo, NOT physical gauge height meters.
2. **Percentile Risk Proxies**: Danger levels are station-specific historical training period percentiles (p90=Yellow, p97=Orange, p99.5=Red), NOT official CWC stage thresholds.
3. **Daily Temporal Resolution**: Training dataset consists of 131,490 daily samples (1990–2025 across 10 stations), matching GloFAS update rates.

---

## Metrics & Validation Summary (1990–2025 Daily Data)

### Protocol (A): Time Split with 7-Day Gap (80% Train / 20% Test)
- **1-Day Lead ($t+1\text{d}$)**:
  - **LightGBM Accuracy**: **87.78%** | **Macro F1**: **81.40%**
  - **Shallow Tree Baseline**: Accuracy 86.12% | Macro F1 78.96%
  - **Persistence Baseline**: Accuracy 90.00% | Macro F1 84.08%
  - **Threshold Rule Benchmark**: Accuracy 63.08% | Macro F1 51.80%
  - **Orange/Red Alert False Alarm Rate (FAR)**: **4.68%**
  - **Orange/Red Alert Missed Event Rate (MER)**: **13.96%** (High-Risk Recall: **86.04%**)
- **2-Day Lead ($t+2\text{d}$)**: Accuracy **81.64%** | Macro F1 **72.87%**
- **3-Day Lead ($t+3\text{d}$)**: Accuracy **77.23%** | Macro F1 **66.01%**

### Protocol (B): Genuinely Out-of-Sample Held-Out 2018 Flood Event Set (with 95% CIs)
- **Training**: Strictly non-2018 data (excluding 2017-12-25 to 2019-01-07 buffer).
- **Test Set Accuracy**: **90.63%**
- **Test Set Macro F1**: **84.71%** (95% CI: **[80.26%, 88.24%]** vs Persistence 85.58% [81.31%, 89.83%])
- **Orange/Red High-Risk Recall**: **91.40%** (vs Persistence 87.21%)
- **August 2018 Warning Lead Time**: Median of **2 Days (48 Hours)** prior to peak discharge deluge across Kerala river stations.

### Protocol (C): Leave-One-RIVER-Out (LORO) Spatial Generalization
- **Rationale**: Stations on the same river (e.g. `KL-PER-01` and `KL-PER-02`) exhibit high discharge cross-correlation ($r > 0.90$). Standard Leave-One-Station-Out can be optimistic due to spatial correlation; Leave-One-RIVER-Out provides a true spatial generalization benchmark.
- **Held-Out River Basin (Periyar Basin)**:
  - **Accuracy**: **89.85%** | **Macro F1**: **82.10%** | **Orange/Red Recall**: **89.50%**

---

## Training Data & Class Breakdown (131,490 Daily Samples)
- **Train Set Distribution**: `{'Green': 72,237, 'Yellow': 22,271, 'Orange': 8,666, 'Red': 2,026}`
- **Test Set Distribution**: `{'Green': 16,363, 'Yellow': 6,175, 'Orange': 2,778, 'Red': 904}`

---

## Input Features (Available at Time t)
1. `rain_1d`: 1-day daily precipitation (mm)
2. `rain_3d`: 3-day cumulative precipitation (mm)
3. `rain_7d`: 7-day cumulative precipitation (mm)
4. `rain_14d`: 14-day cumulative precipitation (mm)
5. `rain_30d`: 30-day cumulative precipitation (mm)
6. `discharge_m3s`: GloFAS river discharge rate at time t (m³/s)
7. `discharge_rate_of_change_3d`: 3-day rate of change in discharge
8. `antecedent_precipitation_index_7d`: 7-day exponential decay antecedent soil moisture proxy
9. `month`: Month of year (1–12)
10. `day_of_year`: Day of year (1–366)
