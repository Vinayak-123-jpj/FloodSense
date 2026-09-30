"""ML Risk Prediction Explainability Module.

Translates complex model feature weights, rolling rainfall anomalies, and river discharge dynamics
into plain-language human-readable risk driver explanations for UI presentation and alerts.
"""

from typing import List, Dict

def generate_plain_language_explanation(features: Dict[str, float], risk_level: str) -> str:
    """Generates plain-language top-3 factor bullet points driving the risk assessment.
    
    Args:
        features: Dictionary containing rolling rainfall, discharge, and wetness index values.
        risk_level: Predicted risk level ('Green', 'Yellow', 'Orange', 'Red').

    Returns:
        Semicolon-separated string of plain-language driver statements.
    """
    drivers = []
    
    r72 = features.get("rain_sum_72h", 0.0)
    r24 = features.get("rain_sum_24h", 0.0)
    r6 = features.get("rain_sum_6h", 0.0)
    d = features.get("discharge_m3s", 0.0)
    d_roc = features.get("discharge_rate_of_change_24h", 0.0)
    api = features.get("antecedent_wetness_index", 0.0)

    # Factor 1: Cumulative Rainfall
    if r72 >= 150.0:
        drivers.append(f"Severe 72h cumulative rainfall ({r72:.1f} mm) exceeding catchment absorption capacity")
    elif r72 >= 75.0:
        drivers.append(f"Elevated 72h cumulative rainfall ({r72:.1f} mm)")
    elif r24 >= 30.0:
        drivers.append(f"Heavy 24h precipitation spell ({r24:.1f} mm)")
    elif r6 >= 15.0:
        drivers.append(f"Recent intense rainfall burst ({r6:.1f} mm in last 6h)")

    # Factor 2: River Discharge & Flow Velocity
    if d >= 500.0:
        drivers.append(f"Extreme river discharge flow velocity ({d:.1f} m³/s)")
    elif d >= 300.0:
        drivers.append(f"High river discharge ({d:.1f} m³/s) approaching channel danger marks")
    
    if d_roc > 20.0:
        drivers.append(f"Rapidly surging river discharge (+{d_roc:.1f} m³/s rise over 24h)")

    # Factor 3: Antecedent Soil Saturation
    if api >= 40.0:
        drivers.append(f"High antecedent soil saturation (API: {api:.1f}) preventing surface infiltration")
    elif api >= 20.0:
        drivers.append(f"Moderate soil moisture accumulation (API: {api:.1f})")

    # Baseline fallback statement if no critical drivers active
    if not drivers:
        if risk_level == "Green":
            drivers.append("Hydrological parameters within normal seasonal baseline range")
            drivers.append("Stable river discharge with minimal surface runoff")
            drivers.append("Low 72-hour cumulative precipitation forecast")
        else:
            drivers.append(f"Water level approaching warning threshold")
            drivers.append(f"Accumulated watershed runoff: {r72:.1f} mm")

    # Limit to top 3 factors
    return "; ".join(drivers[:3])
