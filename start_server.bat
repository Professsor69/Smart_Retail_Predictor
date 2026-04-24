@echo off
echo.
echo  =============================================
echo    Smart Retail Predictor - Web Server
echo  =============================================
echo.
echo  Starting FastAPI server on http://localhost:8000
echo  Press Ctrl+C to stop.
echo.
cd /d "%~dp0"
venv\Scripts\python.exe -m uvicorn api.app:app --reload --port 8000
pause
