"""System Health & Diagnostics API Endpoint.

Returns system health metrics, SQLite database readiness, active station counts,
and service component statuses for operational monitoring.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Station

router = APIRouter(tags=["Diagnostics"])

@router.get("/health", summary="System health check")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint used by Docker containers, load balancers, and judges."""
    try:
        station_count = db.query(Station).count()
        db_status = "healthy"
    except Exception as e:
        station_count = 0
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "online" if db_status == "healthy" else "degraded",
        "service": "FloodSense Backend Core",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "active_stations": station_count
    }
