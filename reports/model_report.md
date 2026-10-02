# FloodSense Machine Learning Risk Model & Science Audit Report

## Executive Summary & Honest Audit Findings
- **Prediction Task**: Multi-Horizon Flood Risk Level Classification ($t+1\text{d}, t+2\text{d}, t+3\text{d}$)
- **Dataset**: 144,639 Daily Hydrological Rows (1990–2025 across 11 stations in Kerala & Assam)
- **Data Leakage Audit Status**: **PASSED (3 Validation Protocols)**
- **Held-Out 2018 Test Accuracy**: **90.36%**
- **Held-Out 2018 Macro F1-Score**: **83.57%** (95% CI: [81.08%, 85.54%] vs Persistence F1: 85.01%)
- **Orange/Red High-Risk Recall**: **90.93%**
- **False Alarm Rate (Orange/Red Alerts)**: **4.15%**
- **August 2018 Warning Lead Time**: Median of **2 Days (48 Hours)** prior to peak deluge across Kerala gauging stations.

---

## 1. Technical Disclaimers & Data Science Audit
> [!IMPORTANT]
> **GloFAS Modeled Discharge**: River discharge ($m^3/s$) is derived from Open-Meteo GloFAS reanalysis modeling, NOT physical gauge height meters.
> **Percentile Risk Proxies**: Station danger levels are defined using historical training period discharge percentiles (p90=Yellow, p97=Orange, p99.5=Red), NOT official CWC stage thresholds.
> **Daily Temporal Resolution**: Data consists of 144,639 daily samples from 1990 to 2025 across 11 stations.
> **Out-of-Training-Range Limitation**: 2018 peak discharge exceeded the 1990–2017 historical maximum at several Kerala stations (e.g. Aluva, Neeleswaram, Chalakudy), so the held-out flood is partly out of the training range; decision tree models split on static feature thresholds and cannot extrapolate beyond training set maxima.

---

## 2. Multi-Horizon Time-Split Performance (80% Train / 20% Test, 7-Day Gap)

| Horizon | Model / Baseline | Accuracy | Macro F1 | False Alarm Rate (FAR) | Missed Event Rate (MER) | High-Risk Recall |
|---|---|---|---|---|---|---|
| **t + 1d (24h)** | **LightGBM (Primary)** | **88.02%** | **81.01%** | **4.48%** | **14.55%** | **85.45%** |
| | Logistic Regression Baseline | 85.37% | 58.29% | 3.80% | 35.31% | 64.69% |
| | Persistence Baseline | 90.22% | 83.84% | 3.33% | 13.09% | 86.91% |
| | Threshold Rule Benchmark | 62.31% | 50.02% | 27.45% | 6.37% | 93.63% |
| **t + 2d (48h)** | **LightGBM (Primary)** | **81.91%** | **72.50%** | **6.33%** | **21.72%** | **78.28%** |
| | Persistence Baseline | 83.09% | 71.76% | 5.70% | 23.43% | 76.57% |
| **t + 3d (72h)** | **LightGBM (Primary)** | **77.77%** | **65.79%** | **7.81%** | **27.62%** | **72.38%** |
| | Persistence Baseline | 77.81% | 62.96% | 7.36% | 32.06% | 67.94% |

---

## 3. Held-Out 2018 Flood Event Validation (with 95% CIs)
Year 2018 (including a 7-day safety buffer on each side: 2017-12-25 to 2019-01-07) was strictly excluded from training.
- **Accuracy**: **90.36%**
- **Macro F1**: **83.57%** (95% CI: **[81.08%, 85.54%]** vs Persistence 85.01% [82.71%, 86.84%])
- **High-Risk Recall**: **90.93%** (vs Persistence 86.90%)
- **Warning Lead Time**: **2 Days (48 Hours)** prior to peak August 2018 flood deluge.

---

## 4. Leave-One-RIVER-Out (LORO) Spatial Validation
Stations on the same river (e.g. `KL-PER-01` and `KL-PER-02`) exhibit high discharge cross-correlation ($r > 0.90$). Standard Leave-One-Station-Out can be optimistic due to spatial correlation; Leave-One-RIVER-Out provides a true spatial generalization benchmark.
- **Periyar River Basin Held-Out**: Accuracy **88.75%** | Macro F1 **79.57%** | High-Risk Recall **85.44%**

---

## 4. Confusion Matrix & Feature Importance
![Confusion Matrix](confusion_matrix.png)
![Feature Importance](feature_importance.png)

---

## 5. Kerala August 2018 Backtest
![Kerala 2018 Backtest](kerala_2018_backtest.png)
