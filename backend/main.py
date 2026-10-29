"""
DataPilot AI - FastAPI Application Entry Point
Unifies data ingestion, profiling, smart data cleaning, chart recommendation,
DuckDB analytical SQL, grounded AI analyst, Scikit-learn ML lab, and dynamic reporting.
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import (
    APP_NAME, APP_SUBTITLE, VERSION, ALLOWED_ORIGINS,
    GEMINI_API_KEY, GROQ_API_KEY, OPENAI_API_KEY
)
from backend.services.dataset_store import dataset_store
from backend.api.datasets import router as datasets_router
from backend.api.cleaning import router as cleaning_router
from backend.api.charts import router as charts_router
from backend.api.sql import router as sql_router
from backend.api.analyst import router as analyst_router
from backend.api.ml import router as ml_router
from backend.api.reports import router as reports_router

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title=f"{APP_NAME} — {APP_SUBTITLE}",
    description="End-to-end Academic Data Science and Analytics Workspace API",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Narrow CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(datasets_router)
app.include_router(cleaning_router)
app.include_router(charts_router)
app.include_router(sql_router)
app.include_router(analyst_router)
app.include_router(ml_router)
app.include_router(reports_router)


# System & Settings endpoints
@app.get("/api/health", summary="Health check and status")
async def health_check():
    return {
        "status": "healthy",
        "app_name": APP_NAME,
        "version": VERSION,
        "active_datasets_count": len(dataset_store.list_all())
    }


@app.get("/api/settings", summary="Get application configuration and active theme")
async def get_settings():
    return {
        "app_name": APP_NAME,
        "app_subtitle": APP_SUBTITLE,
        "version": VERSION,
        "theme": {
            "name": "Professional SaaS",
            "sidebar_bg": "#222225",
            "workspace_bg": "#E8E8E8",
            "panel_bg": "#FFFFFF",
            "primary_text": "#202124",
            "secondary_text": "#62636B",
            "sidebar_text": "#FFFFFF",
            "sidebar_secondary_text": "#C6C6CC",
            "primary_accent": "#D8F45B",
            "secondary_accent": "#B9ADF5",
            "border_color": "#D5D7DC"
        },
        "llm_providers": {
            "gemini_configured": bool(GEMINI_API_KEY),
            "groq_configured": bool(GROQ_API_KEY),
            "openai_configured": bool(OPENAI_API_KEY),
            "active_mode": "LLM Assisted" if (GEMINI_API_KEY or GROQ_API_KEY or OPENAI_API_KEY) else "100% Offline Deterministic"
        }
    }


# Mount Static Frontend Files
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/", summary="Serve Single Page Application (SPA)")
async def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse({
        "message": f"Welcome to {APP_NAME} API. Please ensure the frontend files are located in {FRONTEND_DIR}."
    })


if __name__ == "__main__":
    import uvicorn
    from backend.core.config import HOST, PORT
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)

