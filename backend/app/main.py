import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.database import engine, Base
from backend.app.routers import auth, health, goals, achievements, notifications, analytics

# Auto-create tables on startup (no migrations required for quick local runs)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PulseFit API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits all origins for simplified local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(goals.router, prefix="/api")
app.include_router(achievements.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

# Static folders mount paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount avatar uploads folder
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Mount assets folder for styles and client js files
ASSETS_DIR = os.path.join(FRONTEND_DIR, "assets")
if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

# Default landing page redirect
@app.get("/")
def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# Mount frontend files at root (html=True allows matching pages like /login.html)
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
