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
            "outbox_logged": a.outbox_logged
        }
        result.append(AlertResponse(**res_dict))

    return result

@router.post("/clear", summary="Clear or acknowledge alert outbox logs")
def clear_alerts(db: Session = Depends(get_db)):
    """Clears all historical alerts from outbox display."""
    db.query(Alert).delete()
    db.commit()
    return {"status": "success", "message": "Alert outbox logs cleared successfully."}
