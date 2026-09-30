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

