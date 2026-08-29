Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "CampusMind Backend Setup & Runner (PowerShell)" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

Set-Location $PSScriptRoot

if (-not (Test-Path "venv")) {
    Write-Host "[1/3] Creating virtual environment (venv)..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "[2/3] Activating virtual environment & installing dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "[3/3] Seeding Database..." -ForegroundColor Yellow
python seed.py

Write-Host "======================================================" -ForegroundColor Green
Write-Host "Starting FastAPI Server on http://127.0.0.1:8000 ..." -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
python -m uvicorn app.main:app --reload --port 8000
