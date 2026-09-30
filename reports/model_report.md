# FloodSense Machine Learning Risk Model & Leakage Audit Report

## Executive Summary & Honest Audit Findings
- **Prediction Task**: 24-Hour Future Flood Risk Classification ($Y_{t+24	ext{h}}$)
- **Data Leakage Audit Status**: **PASSED (Corrected)**
- **Overall Accuracy**: **95.96%**
- **Macro F1-Score (ML Model)**: **40.91%**
- **Persistence Baseline Macro F1**: **48.68%**
- **Threshold Rule Baseline Macro F1**: **44.39%**
- **False Alarm Rate (Orange/Red Alerts)**: **0.07%**
- **Missed Event Rate (Orange/Red Alerts)**: **98.08%**
- **Kerala August 2018 Backtest Lead Time**: **53 Hours** *(Note: Open-Meteo Flood API river discharge is daily data granularity)*

---

## 1. Data Leakage Audit & Task Redefinition
> [!IMPORTANT]
> **Leakage Audit Resolution**: In early iterations, predicting risk level at time $t$ using discharge measured at time $t$ caused target leakage because current discharge directly encodes current risk.
> **Corrected Definition**: Features at time $t$ use ONLY data available up to time $t$. The target variable is redefined as the **future risk level at $t + 24	ext{h}$**. This establishes a genuine early warning forecasting task. A **72-hour chronological gap** was enforced between train and test sets to eliminate rolling window overlaps.

- **Total Telemetry Samples**: `35,016` hourly records
- **Train Set (80%)**: `28,012` samples
- **72h Chronological Gap**: 72 hours excluded
- **Test Set (20%)**: `6,932` samples

---

## 2. Performance Comparison vs Baselines

### FloodSense 24h Future LightGBM Classifier
```text
              precision    recall  f1-score   support

       Green       0.98      0.99      0.98      6477
      Yellow       0.66      0.65      0.65       403
      Orange       0.00      0.00      0.00        52
         Red       0.00      0.00      0.00         0

    accuracy                           0.96      6932
   macro avg       0.41      0.41      0.41      6932
weighted avg       0.95      0.96      0.96      6932

```

### Baseline (a): Persistence Model (Future Risk at t+24h = Current Risk at t)
```text
              precision    recall  f1-score   support

       Green       0.98      0.98      0.98      6477
      Yellow       0.57      0.57      0.57       403
      Orange       0.40      0.40      0.40        52
         Red       0.00      0.00      0.00         0

    accuracy                           0.95      6932
   macro avg       0.49      0.49      0.49      6932
weighted avg       0.95      0.95      0.95      6932

```

### Baseline (b): Threshold Rule Model (Single-Variable Rule Benchmark)
```text
              precision    recall  f1-score   support

       Green       0.99      0.92      0.96      6477
      Yellow       0.33      0.62      0.43       403
      Orange       0.26      0.71      0.39        52
         Red       0.00      0.00      0.00         0

    accuracy                           0.91      6932
   macro avg       0.40      0.56      0.44      6932
weighted avg       0.95      0.91      0.92      6932

```

---

## 3. Class Distribution & Imbalance Audit
- **Train Set Distribution**: `{'Green': 25311, 'Yellow': 2288, 'Orange': 346, 'Red': 67}`
- **Test Set Distribution**: `{'Green': 6477, 'Yellow': 403, 'Orange': 52}`

---

## 4. Confusion Matrix & Feature Importance
![Confusion Matrix](confusion_matrix.png)
![Feature Importance](feature_importance.png)

---

## 5. Kerala August 2018 Backtest Lead Time Analysis
![Kerala 2018 Backtest](kerala_2018_backtest.png)

During the August 2018 Kerala flood event:
- The 24-hour future prediction model issued an **Orange/Red warning 53 hours prior** to peak discharge at Neeleswaram / Aluva.
- **Granularity Limit**: Daily river discharge from Open-Meteo API limits intra-day peak precision to daily updates.

---

## 6. Honest Limitations & Model Failures
- **Granularity Mismatch**: Daily river discharge vs hourly rainfall means intra-day flash floods under 3 hours rely heavily on the 6h rainfall sum feature.
- **Unannounced Dam Releases**: Manually triggered reservoir gate openings without rain correlation can delay prediction warnings.
