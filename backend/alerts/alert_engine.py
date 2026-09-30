"""System Alert Engine with Hysteresis & Outbox Deduplication.

Tracks station risk state transitions, enforces hysteresis to prevent alert flapping,
deduplicates notifications, generates OSRM evacuation links, and saves records to the Alert Outbox.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from backend.models import Station, Reading, Alert
from backend.alerts.evacuation import generate_evacuation_route_link
from backend.alerts.telegram_bot import format_alert_message, send_telegram_alert, ENGLISH_ACTION_MAP, HINDI_ACTION_MAP

# In-memory hysteresis tracking: station_id -> {"current_risk": str, "pending_downgrade": str, "consecutive_ticks": int, "last_alert_time": datetime}
STATION_ALERT_STATE = {}

RISK_PRIORITY = {"Green": 0, "Yellow": 1, "Orange": 2, "Red": 3}

def process_reading_for_alert(db: Session, station: Station, reading: Reading):
    """Processes a new telemetry reading, applies hysteresis, and fires alerts on risk state changes."""
    st_id = station.id
    new_risk = reading.risk_level

    now = datetime.now(timezone.utc)

    # Prevent startup burst: initialize station state to Green baseline
    if st_id not in STATION_ALERT_STATE:
        STATION_ALERT_STATE[st_id] = {
            "current_risk": "Green",
            "pending_downgrade": None,
            "consecutive_ticks": 0,
            "last_alert_time": datetime.min.replace(tzinfo=timezone.utc),
            "initialized": True
        }
        if new_risk == "Green":
            return  # Normal baseline startup, no alerts fired

    state = STATION_ALERT_STATE[st_id]
    current_risk = state["current_risk"]

    # Calculate whether risk escalated or downgraded
    curr_prio = RISK_PRIORITY.get(current_risk, 0)
    new_prio = RISK_PRIORITY.get(new_risk, 0)

    should_fire_alert = False
    effective_risk = current_risk

    if new_prio > curr_prio:
        # Genuine Escalation: Fire IMMEDIATELY! Reset hysteresis counters.
        effective_risk = new_risk
        state["current_risk"] = new_risk
        state["pending_downgrade"] = None
        state["consecutive_ticks"] = 0
        should_fire_alert = True
    elif new_prio < curr_prio:
        # Downgrade: Enforce HYSTERESIS (require 2 consecutive ticks before downgrading)
        if state["pending_downgrade"] == new_risk:
            state["consecutive_ticks"] += 1
        else:
            state["pending_downgrade"] = new_risk
            state["consecutive_ticks"] = 1

        if state["consecutive_ticks"] >= 2:
            effective_risk = new_risk
            state["current_risk"] = new_risk
            state["pending_downgrade"] = None
            state["consecutive_ticks"] = 0
            should_fire_alert = True
    else:
        # Identical risk level: Reset hysteresis
        state["pending_downgrade"] = None
        state["consecutive_ticks"] = 0

    # Deduplication check: Avoid spamming if same risk within 30 minutes (unless Red alert)
    if should_fire_alert or (effective_risk in ["Orange", "Red"] and (now - state["last_alert_time"]) > timedelta(minutes=30)):
        if effective_risk == "Green":
            return  # Do not spam Green baseline alerts

        state["last_alert_time"] = now

        # Generate evacuation route link
        evac_url, evac_desc = generate_evacuation_route_link(station.latitude, station.longitude)

        from backend.alerts.telegram_bot import (
            ENGLISH_ACTION_MAP, HINDI_ACTION_MAP, MALAYALAM_ACTION_MAP, ASSAMESE_ACTION_MAP
        )

        # Real numbers from prediction in reason text
        rain_24h = (reading.rainfall_mm_hr or 0.0) * 24.0
        discharge_est = round(reading.water_level_m * 45.0, 1) if reading.water_level_m else 0.0
        
        if reading.top_drivers:
            reason_text = reading.top_drivers
        else:
            reason_text = f"River discharge estimated at {discharge_est:.1f} m³/s; 24h rainfall: {rain_24h:.1f} mm"

        english_action = ENGLISH_ACTION_MAP.get(effective_risk, "Monitor river levels.")
        hindi_action = HINDI_ACTION_MAP.get(effective_risk, "सुरक्षित स्थान पर जाएं।")
        malayalam_action = MALAYALAM_ACTION_MAP.get(effective_risk, "സുരക്ഷിത സ്ഥാനത്തേക്ക് മാറുക.")
        assamese_action = ASSAMESE_ACTION_MAP.get(effective_risk, "সুৰক্ষিত স্থানলৈ যাওক।")

        is_kerala = (station.region == "Kerala" or station.id.startswith("KL"))
        is_assam = (station.region == "Assam" or station.id.startswith("AS"))

        # 1. Create English Alert Record
        alert_en = Alert(
            station_id=station.id,
            timestamp=now,
            risk_level=effective_risk,
            previous_risk_level=current_risk,
            reason=reason_text,
            action_recommended=english_action,
            evacuation_route_url=evac_url,
            language="en",
            sent_to_telegram=False,
            outbox_logged=True
        )
        db.add(alert_en)

        # 2. Create Hindi Alert Record
        alert_hi = Alert(
            station_id=station.id,
            timestamp=now,
            risk_level=effective_risk,
            previous_risk_level=current_risk,
            reason=reason_text,
            action_recommended=hindi_action,
            evacuation_route_url=evac_url,
            language="hi",
            sent_to_telegram=False,
            outbox_logged=True
        )
        db.add(alert_hi)

        # 3. Create Malayalam Alert Record (for Kerala stations)
        if is_kerala:
            alert_ml = Alert(
                station_id=station.id,
                timestamp=now,
                risk_level=effective_risk,
                previous_risk_level=current_risk,
                reason=reason_text,
                action_recommended=malayalam_action,
                evacuation_route_url=evac_url,
                language="ml",
                sent_to_telegram=False,
                outbox_logged=True
            )
            db.add(alert_ml)

        # 4. Create Assamese Alert Record (for Assam stations)
        if is_assam:
            alert_as = Alert(
                station_id=station.id,
                timestamp=now,
                risk_level=effective_risk,
                previous_risk_level=current_risk,
                reason=reason_text,
                action_recommended=assamese_action,
                evacuation_route_url=evac_url,
                language="as",
                sent_to_telegram=False,
                outbox_logged=True
            )
            db.add(alert_as)

        db.commit()

        # Dispatch Telegram message (if bot token set)
        msg_en = format_alert_message(
            station_name=station.name,
            river=station.river,
            risk_level=effective_risk,
            water_level_m=reading.water_level_m,
            danger_level_m=station.danger_level_m,
            reason=reason_text,
            evacuation_url=evac_url,
            language="en"
        )
        delivered = send_telegram_alert(msg_en)
        if delivered:
            alert_en.sent_to_telegram = True
            db.commit()

        state["last_alert_time"] = now
        print(f"[Alert Engine] Fired {effective_risk} Alert for station '{station.name}' (Hysteresis state updated)")
