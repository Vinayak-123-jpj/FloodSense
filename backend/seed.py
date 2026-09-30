"""Database Seeding Script.

Populates initial station metadata and default simulation parameters
from data/stations_metadata.json into the database.
"""

import json
import os
from datetime import datetime, timezone
from backend.database import SessionLocal, engine, Base
from backend.models import Station, SimulationState

def seed_database():
    """Reads JSON station metadata and populates SQLite database tables."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if stations already exist
        if db.query(Station).count() == 0:
            metadata_path = os.path.join(os.path.dirname(__file__), "..", "data", "stations_metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r", encoding="utf-8") as f:
                    stations_data = json.load(f)
                    for item in stations_data:
                        station = Station(
                            id=item["id"],
                            name=item["name"],
                            region=item["region"],
                            river=item["river"],
                            latitude=item["latitude"],
                            longitude=item["longitude"],
                            elevation_m=item["elevation_m"],
                            warning_level_m=item["warning_level_m"],
                            danger_level_m=item["danger_level_m"],
                            normal_level_m=item["normal_level_m"],
                            description=item.get("description", "")
                        )
                        db.add(station)
                print(f"[Seed] Successfully seeded {len(stations_data)} stations.")

        # Ensure default simulation state exists
        sim_state = db.query(SimulationState).first()
        if not sim_state:
            sim_state = SimulationState(
                id=1,
                is_running=True,
                speed=1.0,
                current_scenario="live",
                simulated_time=datetime.now(timezone.utc),
                rain_multiplier=1.0
            )
            db.add(sim_state)
            print("[Seed] Created default simulation state.")

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[Seed Error] Failed to seed database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
