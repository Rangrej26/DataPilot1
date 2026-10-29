# DataPilot AI PowerShell Launch Script
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "Starting DataPilot AI - Professional FastAPI Workspace" -ForegroundColor Green
Write-Host "Web Application: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

Set-Location -Path $PSScriptRoot

Start-Process "http://127.0.0.1:8000"

if (Test-Path ".\.venv\Scripts\python.exe") {
    Write-Host "Using project virtual environment (.venv)..." -ForegroundColor Yellow
    & ".\.venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
} else {
    Write-Host "Using system Python..." -ForegroundColor Yellow
    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
}
