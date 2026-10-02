"""FloodSense FastAPI Core Backend Application.

Main entrypoint configuring OpenAPI documentation, CORS middleware, REST API routers,
WebSocket live telemetry streaming, and APScheduler virtual sensor background service.
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from backend.config import settings
from backend.seed import seed_database
from backend.sensor_simulator import SensorNodeSimulator
from backend.api import stations, readings, forecast, alerts, simulate, health, websocket

# Background scheduler instance for virtual sensor simulation ticks
scheduler = BackgroundScheduler()
simulator = SensorNodeSimulator()

def run_simulation_step():
    """Background task function executing virtual sensor ticks."""
    try:
        simulator.simulate_tick(use_direct_db=True)
    except Exception as e:
        print(f"[Simulation Tick Error] {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI application lifecycle context manager."""
    # 1. Seed database tables and metadata
    seed_database()
    
    # 2. Start APScheduler background simulator
    scheduler.add_job(run_simulation_step, 'interval', seconds=settings.SIM_INTERVAL_SECONDS, id="sensor_sim_job")
    scheduler.start()
    print("[Lifespan] FloodSense backend started with background virtual sensor simulator.")

    yield

    # Shutdown background scheduler
    if scheduler.running:
        scheduler.shutdown()
    print("[Lifespan] FloodSense backend shut down cleanly.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Software-only Flood Early-Warning API for FOSSEE Open Hardware National Make-A-Thon 2026. "
        "Provides REST endpoints for station telemetry, 72h hydrological forecasts, "
        "ML risk predictions, multilingual alerts, and WebSocket live updates."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for local development and Docker frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api prefix
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(stations.router, prefix=settings.API_V1_STR)
app.include_router(readings.router, prefix=settings.API_V1_STR)
app.include_router(forecast.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(simulate.router, prefix=settings.API_V1_STR)

# Register WebSocket router at root /ws/live
app.include_router(websocket.router)

# Mount compiled React frontend SPA if dist folder exists
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException

DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if not os.path.exists(DIST_DIR):
    DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist"))

if os.path.exists(DIST_DIR):
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("ws/") or full_path in ["docs", "redoc", "openapi.json"]:
            raise HTTPException(status_code=404, detail="Not Found")
        target_file = os.path.join(DIST_DIR, full_path)
        if os.path.exists(target_file) and os.path.isfile(target_file):
            return FileResponse(target_file)
        return FileResponse(os.path.join(DIST_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)
