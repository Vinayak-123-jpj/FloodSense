"""SQLAlchemy Database ORM Schema Models.

Defines relational data tables for Monitoring Stations, High-Frequency Telemetry Readings,
System Alerts with Evacuation Guidance, and Virtual Simulation Control State.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from backend.database import Base

class Station(Base):
    """Hydrological river monitoring station metadata."""
    __tablename__ = "stations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    region = Column(String, nullable=False) # e.g. "Kerala", "Assam"
    river = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation_m = Column(Float, nullable=False, default=10.0)
    warning_level_m = Column(Float, nullable=False)
    danger_level_m = Column(Float, nullable=False)
    normal_level_m = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    readings = relationship("Reading", back_populates="station", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="station", cascade="all, delete-orphan")


class Reading(Base):
    """High-frequency telemetry reading sent by physical or virtual sensor node."""
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String, ForeignKey("stations.id"), index=True, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    water_level_cm = Column(Float, nullable=False)
    water_level_m = Column(Float, nullable=False)
    rainfall_mm_hr = Column(Float, nullable=False, default=0.0)
    discharge_m3s = Column(Float, nullable=True, default=0.0)
    battery_pct = Column(Float, nullable=False, default=100.0)
    rssi = Column(Integer, nullable=False, default=-65)
    risk_level = Column(String, nullable=False, default="Green") # Green, Yellow, Orange, Red
    sensor_status = Column(String, nullable=False, default="OK") # OK, DEGRADED, FAULT
    top_drivers = Column(Text, nullable=True) # JSON list or plain text drivers

    station = relationship("Station", back_populates="readings")


class Alert(Base):
    """System-generated flood warning alert with hysteresis and outbox tracking."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String, ForeignKey("stations.id"), index=True, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    risk_level = Column(String, nullable=False)
    previous_risk_level = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    action_recommended = Column(Text, nullable=False)
    evacuation_route_url = Column(Text, nullable=True)
    language = Column(String, nullable=False, default="en") # en, hi
    sent_to_telegram = Column(Boolean, default=False)
    outbox_logged = Column(Boolean, default=True)

    station = relationship("Station", back_populates="alerts")


class SimulationState(Base):
    """Global virtual sensor simulation engine state."""
    __tablename__ = "simulation_state"

    id = Column(Integer, primary_key=True, default=1)
    is_running = Column(Boolean, default=True)
    speed = Column(Float, default=1.0)
    current_scenario = Column(String, default="live") # live, kerala_2018, assam_2020
    simulated_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    rain_multiplier = Column(Float, default=1.0)
