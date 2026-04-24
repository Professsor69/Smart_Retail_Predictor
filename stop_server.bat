@echo off
echo.
echo  =============================================
echo    Smart Retail Predictor - STOP Server
echo  =============================================
echo.
echo  Killing all Python processes...
taskkill /IM python.exe /F >nul 2>&1
taskkill /IM python3.13.exe /F >nul 2>&1
taskkill /IM python3.exe /F >nul 2>&1
echo.
echo  Done! Server on localhost:8000 is stopped.
echo  You can close this window.
echo.
pause
