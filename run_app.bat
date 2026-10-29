@echo off
title DataPilot AI — Professional Workspace
echo ===================================================================
echo Starting DataPilot AI - Professional FastAPI + HTML/CSS/JS Workspace
echo URL: http://127.0.0.1:8000
echo ===================================================================

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    echo Using project virtual environment (.venv)...
    start http://127.0.0.1:8000
    ".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
) else (
    echo Using system Python...
    start http://127.0.0.1:8000
    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application encountered an issue or was stopped.
    pause
)
