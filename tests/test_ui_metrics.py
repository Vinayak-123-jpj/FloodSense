"""Frontend UI & Metrics Consistency Test.

Verifies that reports/metrics.json and data/thresholds.json contain all required fields
without any undefined, NaN, or missing metric values for rendering on Model & Method page.
"""

import os
import json
import math
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def test_metrics_json_has_no_undefined_or_nan():
    """Fails if any field in reports/metrics.json is 'undefined', NaN, or missing."""
    metrics_path = os.path.join(PROJECT_ROOT, "reports", "metrics.json")
    assert os.path.exists(metrics_path), "reports/metrics.json is missing"

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    # 1. Multi-horizon heldout metrics check
    mh = metrics.get("heldout_2018_multi_horizon", {})
    assert "1d" in mh and "2d" in mh and "3d" in mh, "Missing multi-horizon keys in metrics.json"

    for h in ["1d", "2d", "3d"]:
        models_dict = mh[h]
        for m_key in ["lightgbm", "persistence_baseline", "threshold_baseline"]:
            assert m_key in models_dict, f"Missing {m_key} in horizon {h}"
            m_data = models_dict[m_key]
            for metric in ["macro_f1_pct", "orange_red_recall_pct", "orange_red_precision_pct", "false_alarms_per_station_year"]:
                val = m_data.get(metric)
                assert val is not None, f"Metric {metric} is None in horizon {h} for {m_key}"
                assert not (isinstance(val, float) and math.isnan(val)), f"Metric {metric} is NaN in horizon {h}"
                assert str(val) != "undefined", f"Metric {metric} is 'undefined' in horizon {h}"

    # 2. Per-station 2018 details check
    st_details = metrics.get("station_2018_details", {})
    assert len(st_details) >= 11, "Missing station details in metrics.json"

    for st_id, details in st_details.items():
        assert "actual_orange_red_days_2018" in details, f"Missing actual_orange_red_days_2018 for {st_id}"
        assert "first_warning_date" in details, f"Missing first_warning_date for {st_id}"
        assert "first_threshold_crossing_date" in details, f"Missing first_threshold_crossing_date for {st_id}"
        assert "lead_time_display" in details, f"Missing lead_time_display for {st_id}"

        for k, v in details.items():
            assert str(v) != "undefined", f"Field {k} for {st_id} is string 'undefined'"
            if isinstance(v, float):
                assert not math.isnan(v), f"Field {k} for {st_id} is NaN"

def test_thresholds_json_has_no_undefined_or_nan():
    """Fails if any station threshold in data/thresholds.json is undefined or NaN."""
    thresh_path = os.path.join(PROJECT_ROOT, "data", "thresholds.json")
    assert os.path.exists(thresh_path), "data/thresholds.json is missing"

    with open(thresh_path, "r", encoding="utf-8") as f:
        thresh = json.load(f)

    for st_id, info in thresh.items():
        assert "p90_yellow" in info and info["p90_yellow"] is not None
        assert "p97_orange" in info and info["p97_orange"] is not None
        assert "p99.5_red" in info and info["p99.5_red"] is not None

        for k, v in info.items():
            assert str(v) != "undefined", f"Field {k} for {st_id} is string 'undefined'"
            if isinstance(v, float):
                assert not math.isnan(v), f"Field {k} for {st_id} is NaN"
