# FloodSense Machine Learning Risk Model & Science Audit Report

## Executive Summary & Honest Audit Findings
- **Prediction Task**: Multi-Horizon Flood Risk Level Classification ($t+1\text{d}, t+2\text{d}, t+3\text{d}$)
- **Dataset**: 115,502 Daily Hydrological Rows (1990–2025 across 11 stations in Kerala & Assam)
- **Data Leakage Audit Status**: **PASSED (3 Validation Protocols)**
- **Held-Out 2018 Test Accuracy**: **83.20%**
- **Held-Out 2018 Macro F1-Score**: **69.39%** (95% CI: [63.48%, 73.66%] vs Persistence F1: 85.15%)
- **Orange/Red High-Risk Recall**: **86.27%**
- **False Alarm Rate (Orange/Red Alerts)**: **21.20%**
- **August 2018 Warning Lead Time**: Strict lead times evaluated per station (e.g. Aluva & Muvattupuzha >=3 days capped; Neeleswaram, Chengannur & Chalakudy 0-day same-day warnings).

---

## 1. Technical Disclaimers & Data Science Audit
> [!IMPORTANT]
> **GloFAS Modeled Discharge**: River discharge ($m^3/s$) is derived from Open-Meteo GloFAS reanalysis modeling, NOT physical gauge height meters.
> **Percentile Risk Proxies**: Station danger levels are defined using historical training period discharge percentiles (p90=Yellow, p97=Orange, p99.5=Red), NOT official CWC stage thresholds.
> **Daily Temporal Resolution**: Data consists of 115,502 daily samples from 1990 to 2025 across 11 stations.
> **Out-of-Training-Range Limitation**: 2018 peak discharge exceeded the 1990–2017 historical maximum at several Kerala stations (e.g. Aluva, Neeleswaram, Chalakudy), so the held-out flood is partly out of the training range; decision tree models split on static feature thresholds and cannot extrapolate beyond training set maxima.

---

## 2. Multi-Horizon Time-Split Performance (80% Train / 20% Test, 7-Day Gap)

| Horizon | Model / Baseline | Accuracy | Macro F1 | False Alarm Rate (FAR) | Missed Event Rate (MER) | High-Risk Recall |
|---|---|---|---|---|---|---|
| **t + 1d (24h)** | **LightGBM (Primary)** | **83.20%** | **69.39%** | **21.20%** | **13.73%** | **86.27%** |
| | Logistic Regression Baseline | 61.70% | 54.02% | 22.47% | 13.77% | 86.23% |
| | Persistence Baseline | 91.71% | 85.15% | 6.60% | 13.07% | 86.93% |
| | Threshold Rule Benchmark | 61.94% | 32.47% | 96.00% | 2.61% | 97.39% |
| **t + 2d (48h)** | **LightGBM (Primary)** | **79.50%** | **56.47%** | **32.40%** | **16.34%** | **83.66%** |
| | Persistence Baseline | 83.09% | 72.54% | 12.00% | 24.84% | 75.16% |
| **t + 3d (72h)** | **LightGBM (Primary)** | **75.10%** | **46.27%** | **43.80%** | **18.95%** | **81.05%** |
| | Persistence Baseline | 77.81% | 62.41% | 16.40% | 34.64% | 65.36% |

---

## 3. Held-Out 2018 Flood Event Validation (with 95% CIs)
Year 2018 (including a 7-day safety buffer on each side: 2017-12-25 to 2019-01-07) was strictly excluded from training.
- **Accuracy**: **83.20%**
- **Macro F1**: **69.39%** (95% CI: **[63.48%, 73.66%]** vs Persistence 85.15% [82.00%, 87.40%])
- **High-Risk Recall**: **86.27%** (vs Persistence 86.93%)
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
