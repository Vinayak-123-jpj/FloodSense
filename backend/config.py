"""Backend Application Configuration Module.

Provides centralized configuration parameters for database connections, API paths,
Telegram bot tokens, and simulation parameters.
"""

import os

class Settings:
    PROJECT_NAME: str = "FloodSense Flood Early-Warning System"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./floodsense.db")
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Simulation Parameters
    DEFAULT_SIM_SPEED: float = 1.0
    SIM_INTERVAL_SECONDS: int = 5
    
    # ML Model configuration
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models/flood_risk_model.joblib")
    SCALER_PATH: str = os.getenv("SCALER_PATH", "./models/feature_scaler.joblib")

settings = Settings()
