@echo off
echo ======================================================
echo CampusMind Backend Setup & Runner
echo ======================================================

cd /d "%~dp0"

echo [1/3] Checking / Creating virtual environment...
if not exist "venv" (
    python -m venv venv
)

echo [2/3] Activating virtual environment & installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo [3/3] Running Database Seeder...
python seed.py

echo ======================================================
echo Starting FastAPI Server on http://127.0.0.1:8000 ...
echo ======================================================
python -m uvicorn app.main:app --reload --port 8000
pause
