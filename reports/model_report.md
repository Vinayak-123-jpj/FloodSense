# FloodSense Machine Learning Risk Model & Science Audit Report

## Executive Summary & Honest Audit Findings
- **Prediction Task**: Multi-Horizon Flood Risk Level Classification ($t+1\text{d}, t+2\text{d}, t+3\text{d}$)
- **Dataset**: 131,490 Daily Hydrological Rows (1990–2025 across 10 stations in Kerala & Assam)
- **Data Leakage Audit Status**: **PASSED (3 Validation Protocols)**
- **Held-Out 2018 Test Accuracy**: **90.63%**
- **Held-Out 2018 Macro F1-Score**: **84.71%** (vs Persistence F1: 85.58%)
- **Orange/Red High-Risk Recall**: **91.40%**
- **False Alarm Rate (Orange/Red Alerts)**: **4.11%**
- **August 2018 Warning Lead Time**: Median of **2 Days (48 Hours)** prior to peak deluge across Kerala gauging stations.

---

## 1. Technical Disclaimers & Data Science Audit
> [!IMPORTANT]
> **GloFAS Modeled Discharge**: River discharge ($m^3/s$) is derived from Open-Meteo GloFAS reanalysis modeling, NOT physical gauge height meters.
> **Percentile Risk Proxies**: Station danger levels are defined using historical training period discharge percentiles (p90=Yellow, p97=Orange, p99.5=Red), NOT official CWC stage thresholds.
> **Daily Temporal Resolution**: Data consists of 131,490 daily samples from 1990 to 2025 across 10 stations.

---

## 2. Multi-Horizon Time-Split Performance (80% Train / 20% Test, 7-Day Gap)

| Horizon | Model / Baseline | Accuracy | Macro F1 | False Alarm Rate (FAR) | Missed Event Rate (MER) | High-Risk Recall |
|---|---|---|---|---|---|---|
| **t + 1d (24h)** | **LightGBM (Primary)** | **87.78%** | **81.40%** | **4.68%** | **13.96%** | **86.04%** |
| | Shallow Tree Baseline (depth=2) | 86.12% | 78.96% | 4.82% | 17.54% | 82.46% |
| | Persistence Baseline | 90.00% | 84.08% | 3.47% | 12.76% | 87.24% |
| | Threshold Rule Benchmark | 63.08% | 51.80% | 26.61% | 6.63% | 93.37% |
| **t + 2d (48h)** | **LightGBM (Primary)** | **81.64%** | **72.87%** | **6.71%** | **20.67%** | **79.33%** |
| | Persistence Baseline | 82.69% | 72.05% | 5.98% | 22.92% | 77.08% |
| **t + 3d (72h)** | **LightGBM (Primary)** | **77.23%** | **66.01%** | **8.32%** | **26.72%** | **73.28%** |
| | Persistence Baseline | 77.25% | 63.19% | 7.74% | 31.34% | 68.66% |

---

## 3. Held-Out 2018 Flood Event Validation (with 95% CIs)
Year 2018 (including a 7-day safety buffer on each side: 2017-12-25 to 2019-01-07) was strictly excluded from training.
- **Accuracy**: **90.63%**
- **Macro F1**: **84.71%** (95% CI: **[80.26%, 88.24%]** vs Persistence 85.58% [81.31%, 89.83%])
- **High-Risk Recall**: **91.40%** (vs Persistence 87.21%)
- **Warning Lead Time**: **2 Days (48 Hours)** prior to peak August 2018 flood deluge.

---

## 4. Leave-One-RIVER-Out (LORO) Spatial Validation
Stations on the same river (e.g. `KL-PER-01` and `KL-PER-02`) exhibit high discharge cross-correlation ($r > 0.90$). Standard Leave-One-Station-Out can be optimistic due to spatial correlation; Leave-One-RIVER-Out provides a true spatial generalization benchmark.
- **Periyar River Basin Held-Out**: Accuracy **89.85%** | Macro F1 **82.10%** | High-Risk Recall **89.50%**

---

## 4. Confusion Matrix & Feature Importance
![Confusion Matrix](confusion_matrix.png)
![Feature Importance](feature_importance.png)

---

## 5. Kerala August 2018 Backtest
![Kerala 2018 Backtest](kerala_2018_backtest.png)
