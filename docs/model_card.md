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
3. **Daily Temporal Resolution**: Training dataset consists of 115,502 daily samples (1990–2025 across 11 stations), matching GloFAS update rates.
4. **Out-of-Training-Range Limitation**: 2018 peak discharge exceeded the 1990–2017 historical maximum at several Kerala stations (e.g. Aluva, Neeleswaram, Chalakudy), so the held-out flood is partly out of the training range; decision tree models split on static feature thresholds and cannot extrapolate beyond training set maxima.

---

## Metrics & Validation Summary (1990–2025 Daily Data)

### Protocol (A): Time Split with 7-Day Gap (80% Train / 20% Test)
- **1-Day Lead ($t+1\text{d}$)**:
  - **LightGBM Accuracy**: **88.02%** | **Macro F1**: **81.01%** [79.99%, 82.06%]
  - **Logistic Regression**: Accuracy 85.37% | Macro F1 58.29%
  - **Persistence Baseline**: Accuracy 90.22% | Macro F1 83.84%
  - **Threshold Rule Benchmark**: Accuracy 62.31% | Macro F1 50.02%
  - **Orange/Red Alert False Alarm Rate (FAR)**: **4.48%**
  - **Orange/Red Alert Missed Event Rate (MER)**: **14.55%** (High-Risk Recall: **85.45%**)
- **2-Day Lead ($t+2\text{d}$)**: Accuracy **81.91%** | Macro F1 **72.50%**
- **3-Day Lead ($t+3\text{d}$)**: Accuracy **77.77%** | Macro F1 **65.79%**

### Protocol (B): Genuinely Out-of-Sample Held-Out 2018 Flood Event Set (with 95% CIs)
- **Training**: Strictly non-2018 data (excluding 2017-12-25 to 2019-01-07 buffer).
- **Test Set Accuracy**: **83.20%**
- **Test Set Macro F1**: **69.39%** (95% CI: **[63.48%, 73.66%]** vs Persistence 85.15% [82.0%, 87.4%])
- **Orange/Red High-Risk Recall**: **86.27%** (vs Persistence 86.93%)
- **August 2018 Warning Lead Time**: Strict lead times evaluated per station (e.g. Aluva & Muvattupuzha $\ge 3$ days capped; Neeleswaram, Chengannur & Chalakudy 0-day same-day warnings).

### Protocol (C): Leave-One-RIVER-Out (LORO) Spatial Generalization
- **Rationale**: Stations on the same river (e.g. `KL-PER-01` and `KL-PER-02`) exhibit high discharge cross-correlation ($r > 0.90$). Standard Leave-One-Station-Out can be optimistic due to spatial correlation; Leave-One-RIVER-Out provides a true spatial generalization benchmark.
- **Held-Out River Basin (Periyar Basin)**:
  - **Accuracy**: **88.75%** | **Macro F1**: **79.57%** | **Orange/Red Recall**: **85.44%**

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
