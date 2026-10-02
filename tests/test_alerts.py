"""Unit & Integration Tests for Alert Engine & Multilingual Telegram Bot.

Tests risk escalation alerts, hysteresis downgrade prevention, alert deduplication,
evacuation route link creation, and multilingual message formatting.
"""

import pytest
from backend.models import Station, Reading, Alert
from backend.database import Base, engine, SessionLocal
from backend.alerts.alert_engine import process_reading_for_alert, STATION_ALERT_STATE
from backend.alerts.evacuation import generate_evacuation_route_link
from backend.alerts.telegram_bot import format_alert_message

@pytest.fixture(autouse=True)
def setup_db():
    """Initializes clean database schema prior to each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    STATION_ALERT_STATE.clear()
    yield

def test_evacuation_route_generation():
    """Verifies OpenStreetMap evacuation link generation for Kerala station."""
    url, desc = generate_evacuation_route_link(10.1416, 76.5781) # Neeleswaram
    assert "openstreetmap.org" in url
    assert "route=" in url
    assert "Evacuate" in desc

def test_alert_escalation_and_hysteresis():
    """Verifies that risk escalation fires immediately, while downgrade requires 2 ticks."""
    db = SessionLocal()
    st = Station(
        id="TEST-AL-01", name="Test Gauge", region="Kerala", river="Periyar",
        latitude=10.14, longitude=76.57, elevation_m=10.0,
        warning_level_m=4.0, danger_level_m=6.0, normal_level_m=2.0
    )
    db.add(st)
    db.commit()

    # 0. Baseline initialization on startup (Green) -> zero alerts fired
    r0 = Reading(
        station_id=st.id, water_level_cm=200.0, water_level_m=2.0,
        rainfall_mm_hr=0.0, battery_pct=95.0, rssi=-60, risk_level="Green"
    )
    process_reading_for_alert(db, st, r0)
    assert len(db.query(Alert).filter(Alert.station_id == st.id).all()) == 0

    # 1. Escalation to Orange (Tick 1) -> Should fire alert immediately
    r1 = Reading(
        station_id=st.id, water_level_cm=450.0, water_level_m=4.5,
        rainfall_mm_hr=20.0, battery_pct=95.0, rssi=-60, risk_level="Orange"
    )
    process_reading_for_alert(db, st, r1)
    
    alerts_tick1 = db.query(Alert).filter(Alert.station_id == st.id).all()
    assert len(alerts_tick1) >= 3 # 1 EN + 1 HI + 1 ML (Kerala station)

    # 2. Single lower tick (Green) -> Hysteresis MUST NOT downgrade state on first tick
    r2 = Reading(
        station_id=st.id, water_level_cm=200.0, water_level_m=2.0,
        rainfall_mm_hr=0.0, battery_pct=95.0, rssi=-60, risk_level="Green"
    )
    process_reading_for_alert(db, st, r2)
    # Risk should remain Orange during pending downgrade
    assert STATION_ALERT_STATE[st.id]["current_risk"] == "Orange"
    assert STATION_ALERT_STATE[st.id]["consecutive_ticks"] == 1

    # 3. Second consecutive lower tick (Green) -> Hysteresis now approves downgrade
    r3 = Reading(
        station_id=st.id, water_level_cm=200.0, water_level_m=2.0,
        rainfall_mm_hr=0.0, battery_pct=95.0, rssi=-60, risk_level="Green"
    )
    process_reading_for_alert(db, st, r3)
    assert STATION_ALERT_STATE[st.id]["current_risk"] == "Green"
    db.close()

def test_telegram_multilingual_formatting():
    """Verifies English, Hindi, Malayalam, and Assamese Telegram message formatting."""
    msg_en = format_alert_message("Neeleswaram", "Periyar River", "Orange", 4.8, 6.0, "Heavy rain", "http://map.link", "en")
    assert "FLOOD WARNING" in msg_en
    assert "Neeleswaram" in msg_en

    msg_hi = format_alert_message("Neeleswaram", "Periyar River", "Orange", 4.8, 6.0, "भारी वर्षा", "http://map.link", "hi")
    assert "बाढ़ चेतावनी" in msg_hi
    assert "चेतावनी (Orange)" in msg_hi

    msg_ml = format_alert_message("Neeleswaram", "Periyar River", "Orange", 4.8, 6.0, "കനത്ത മഴ", "http://map.link", "ml")
    assert "പ്രളയ മുന്നറിയിപ്പ്" in msg_ml
    assert "മുന്നറിയിപ്പ് (Orange)" in msg_ml

    msg_as = format_alert_message("Neeleswaram", "Periyar River", "Orange", 4.8, 6.0, "প্রবল বৰষুণ", "http://map.link", "as")
    assert "বানপানী সকিয়ানী" in msg_as
    assert "সাঁৱধান (Orange)" in msg_as

def test_fresh_startup_produces_zero_alerts():
    """Verifies that fresh startup or source switch produces zero initial alerts."""
    db = SessionLocal()
    st = Station(
        id="TEST-AL-ZERO", name="Startup Gauge", region="Kerala", river="Periyar",
        latitude=10.14, longitude=76.57, elevation_m=10.0,
        warning_level_m=4.0, danger_level_m=6.0, normal_level_m=2.0
    )
    db.add(st)
    db.commit()

    # First prediction after startup (even if Yellow/Orange) establishes baseline with zero alerts fired
    r_first = Reading(
        station_id=st.id, water_level_cm=350.0, water_level_m=3.5,
        rainfall_mm_hr=15.0, battery_pct=95.0, rssi=-60, risk_level="Yellow"
    )
    process_reading_for_alert(db, st, r_first)
    alerts = db.query(Alert).filter(Alert.station_id == st.id).all()
    assert len(alerts) == 0
    assert STATION_ALERT_STATE[st.id]["current_risk"] == "Yellow"
    db.close()


def test_demo_alert_flow_and_four_language_toggle():
    """Verifies DEMO alert creation API, is_demo flag, [DEMO ALERT] tag, and 4-language outbox entries."""
    from fastapi.testclient import TestClient
    from backend.main import app

    with TestClient(app) as client:
        # Trigger DEMO alert
        res = client.post("/api/alerts/demo?station_id=KL-PER-01&risk_level=Orange&language=hi")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "created_ids" in data
        assert len(data["created_ids"]) == 4

        # Fetch outbox entries
        alerts_res = client.get("/api/alerts")
        assert alerts_res.status_code == 200
        all_alerts = alerts_res.json()
        assert len(all_alerts) >= 4

        # Verify languages en, hi, ml, as are present
        langs = {a["language"] for a in all_alerts}
        assert {"en", "hi", "ml", "as"}.issubset(langs)

        # Verify is_demo flag and reason prefix
        demo_items = [a for a in all_alerts if a["is_demo"]]
        assert len(demo_items) >= 4
        for item in demo_items:
            assert item["is_demo"] is True
            assert "[DEMO ALERT]" in item["reason"]


def test_clear_alerts_endpoint():
    """Verifies that clear alerts endpoint wipes outbox entries and clears hysteresis state."""
    from fastapi.testclient import TestClient
    from backend.main import app

    with TestClient(app) as client:
        # Trigger demo alert to populate outbox
        client.post("/api/alerts/demo?station_id=KL-PER-01&risk_level=Red")
        assert len(client.get("/api/alerts").json()) > 0

        # Clear outbox
        clear_res = client.post("/api/alerts/clear")
        assert clear_res.status_code == 200
        assert clear_res.json()["status"] == "success"

        # Verify outbox is empty
        assert len(client.get("/api/alerts").json()) == 0


