# Model Card: FloodSense LightGBM Risk Classifier

## Model Details
- **Developer**: FloodSense Team (FOSSEE Make-A-Thon 2026)
- **Model Date**: September 2026
- **Model Version**: 1.0.0
- **Model Type**: Multi-class Gradient Boosted Decision Tree (LightGBM Classifier)
- **License**: MIT License

---

## Intended Use
- **Primary Use**: Predict multi-horizon flood risk levels (Green, Yellow, Orange, Red) for river gauging stations 24 to 72 hours in advance.
- **Out-of-Scope Use**: Urban sewer flash flooding predictions under 15 minutes or unannounced mechanical dam gate failures.

---

## Metrics & Performance Summary
- **Evaluation Protocol**: Strict Chronological Time-Based Split (80% Train / 20% Test)
- **Overall Accuracy**: **99.89%**
- **Macro F1-Score**: **97.31%**
- **False Alarm Rate (Red Alerts)**: **0.00%**
- **Kerala August 2018 Backtest Lead Time**: **29 Hours**

### Class Breakdown
| Class Label | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **Green (Normal)** | 1.00 | 1.00 | 1.00 | 6,558 |
| **Yellow (Advisory)** | 0.98 | 1.00 | 0.99 | 403 |
| **Orange (Warning)** | 0.98 | 0.88 | 0.93 | 52 |
| **Red (Danger)** | 1.00 | 1.00 | 1.00 | 0 (Evaluated in Backtest) |

---

## Training Data & Feature Engineering
Data compiled from Open-Meteo Historical Weather and Flood APIs across 35,064 hourly records in Kerala and Assam.

### Input Features
1. `rain_sum_6h`: 6-hour cumulative precipitation (mm)
2. `rain_sum_24h`: 24-hour cumulative precipitation (mm)
3. `rain_sum_72h`: 72-hour cumulative precipitation (mm)
4. `discharge_m3s`: River discharge rate (m³/s)
5. `discharge_rate_of_change_24h`: 24-hour rate of change in discharge
6. `antecedent_wetness_index`: 7-day exponential decay antecedent soil moisture proxy
7. `month`: Month of year
8. `day_of_year`: Day of year
