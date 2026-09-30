# Model Card: FloodSense LightGBM Risk Classifier

## Model Details
- **Developer**: FloodSense Team (FOSSEE Make-A-Thon 2026)
- **Model Date**: October 2026
- **Model Version**: 2.0.0 (Leakage-Audited 24h Future Lead Time Model)
- **Model Type**: Multi-class Gradient Boosted Decision Tree (LightGBM Classifier)
- **License**: MIT License

---

## Intended Use
- **Primary Use**: Predict multi-horizon flood risk levels (Green, Yellow, Orange, Red) for river gauging stations 24 hours in advance ($Y_{t+24\text{h}}$).
- **Out-of-Scope Use**: Urban sewer flash flooding predictions under 15 minutes or unannounced mechanical dam gate failures.

---

## Metrics & Leakage Audit Summary
- **Data Leakage Audit**: **PASSED**. Target redefined to future risk $Y_{t+24\text{h}}$.
- **Evaluation Protocol**: Strict Chronological Time-Based Split with **72-Hour Gap** (28,012 Train / 6,932 Test)
- **Overall Accuracy**: **95.96%**
- **Macro F1-Score**: **40.91%**
- **Persistence Baseline Macro F1**: **48.68%**
- **Threshold Rule Baseline Macro F1**: **44.39%**
- **False Alarm Rate (Orange/Red Alerts)**: **0.07%**
- **Missed Event Rate (Orange/Red Alerts)**: **98.08%** (high imbalance in 20% future test set)
- **Kerala August 2018 Backtest Lead Time**: **53 Hours** *(Note: Open-Meteo Flood API river discharge is daily data granularity)*

---

## Training Data & Class Distribution
Data compiled from Open-Meteo Historical Weather and Flood APIs across 35,064 hourly records in Kerala and Assam.

### Class Breakdown
- **Train Set Distribution**: `{'Green': 25311, 'Yellow': 2288, 'Orange': 346, 'Red': 67}`
- **Test Set Distribution**: `{'Green': 6477, 'Yellow': 403, 'Orange': 52}`

---

## Input Features (Available at Time t)
1. `rain_sum_6h`: 6-hour cumulative precipitation (mm)
2. `rain_sum_24h`: 24-hour cumulative precipitation (mm)
3. `rain_sum_72h`: 72-hour cumulative precipitation (mm)
4. `discharge_m3s`: River discharge rate at time t (m³/s)
5. `discharge_rate_of_change_24h`: 24-hour rate of change in discharge
6. `antecedent_wetness_index`: 7-day exponential decay antecedent soil moisture proxy
7. `month`: Month of year
8. `day_of_year`: Day of year
