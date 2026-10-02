"""Alert Query & Outbox Management API Endpoints.

Provides REST endpoints to retrieve system alert logs, Telegram message history,
and localized evacuation routes for high-risk flood conditions.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Alert, Station
from backend.schemas import AlertResponse

router = APIRouter(prefix="/alerts", tags=["System Alerts & Outbox"])

@router.get("", response_model=List[AlertResponse], summary="List alert history and outbox entries")
def get_alerts(
    station_id: Optional[str] = Query(None, description="Optional station ID filter"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Retrieves generated flood warning alerts from database and outbox log."""
    query = db.query(Alert)
    if station_id:
        query = query.filter(Alert.station_id == station_id)
    
    alerts = query.order_by(Alert.timestamp.desc()).limit(limit).all()

    result = []
    for a in alerts:
        st = db.query(Station).filter(Station.id == a.station_id).first()
        res_dict = {
            "id": a.id,
            "station_id": a.station_id,
            "station_name": st.name if st else a.station_id,
            "timestamp": a.timestamp,
            "risk_level": a.risk_level,
            "previous_risk_level": a.previous_risk_level,
            "reason": a.reason,
            "action_recommended": a.action_recommended,
            "evacuation_route_url": a.evacuation_route_url,
            "language": a.language,
            "sent_to_telegram": a.sent_to_telegram,
            "outbox_logged": a.outbox_logged,
            "is_demo": getattr(a, "is_demo", False)
        }
        result.append(AlertResponse(**res_dict))

    return result

@router.post("/clear", summary="Clear or acknowledge alert outbox logs")
def clear_alerts(db: Session = Depends(get_db)):
    """Clears all historical alerts from outbox display and resets state baseline."""
    from backend.alerts.alert_engine import STATION_ALERT_STATE
    STATION_ALERT_STATE.clear()
    db.query(Alert).delete()
    db.commit()
    return {"status": "success", "message": "Alert outbox logs cleared successfully."}

@router.post("/demo", summary="Trigger a DEMO flood warning alert for testing/preview")
def create_demo_alert(
    station_id: str = Query("KL-PER-01"),
    risk_level: str = Query("Orange"),
    language: str = Query("en"),
    db: Session = Depends(get_db)
):
    """Creates clearly marked DEMO alerts across all supported languages (English, Hindi, Malayalam, Assamese) for preview."""
    from datetime import datetime, timezone
    from backend.alerts.evacuation import generate_evacuation_route_link
    from backend.alerts.telegram_bot import (
        ENGLISH_ACTION_MAP, HINDI_ACTION_MAP, MALAYALAM_ACTION_MAP, ASSAMESE_ACTION_MAP
    )

    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        station = db.query(Station).first()
    
    st_id = station.id if station else station_id
    st_name = station.name if station else station_id
    st_lat = station.latitude if station else 10.1416
    st_lon = station.longitude if station else 76.5781
    p97 = station.warning_level_m * 45.0 if station else 310.0

    evac_url, _ = generate_evacuation_route_link(st_lat, st_lon)
    now = datetime.now(timezone.utc)

    demo_reason = (
        f"[DEMO ALERT] Target: D+1 Model Forecast. "
        f"Predicted discharge 425.0 m³/s crossed p97 threshold ({p97:.1f} m³/s). "
        f"Top Drivers: 7-day cumulative rain 165.0 mm; 3-day discharge rate of change +85.0 m³/s."
    )

    lang_actions = {
        "en": ENGLISH_ACTION_MAP.get(risk_level, "Prepare for evacuation."),
        "hi": HINDI_ACTION_MAP.get(risk_level, "सुरक्षित स्थान पर जाएं।"),
        "ml": MALAYALAM_ACTION_MAP.get(risk_level, "സുരക്ഷിത സ്ഥാനത്തേക്ക് മാറുക."),
        "as": ASSAMESE_ACTION_MAP.get(risk_level, "সুৰক্ষিত স্থানলৈ যাওক।")
    }

    created_ids = []
    # Create DEMO alerts for all 4 supported languages so language toggle previews work seamlessly
    for lang_code, action_str in lang_actions.items():
        alert = Alert(
            station_id=st_id,
            timestamp=now,
            risk_level=risk_level,
            previous_risk_level="Green",
            reason=demo_reason,
            action_recommended=action_str,
            evacuation_route_url=evac_url,
            language=lang_code,
            sent_to_telegram=False,
            outbox_logged=True,
            is_demo=True
        )
        db.add(alert)
        db.flush()
        created_ids.append(alert.id)

    db.commit()

    return {
        "status": "success",
        "message": f"DEMO Alert created for {st_name} across all 4 languages (EN, HI, ML, AS)",
        "alert_id": created_ids[0],
        "created_ids": created_ids
    }
