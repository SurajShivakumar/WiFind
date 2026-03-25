@echo off
echo ============================================
echo WiFi Heatmap Server for Windows PC
echo ============================================
echo.
echo Starting server on http://localhost:5000
echo.
echo Make sure Flask is installed:
echo   pip install flask flask-socketio
echo.
echo ============================================

cd /d "%~dp0"
python wifi_heatmap_server.py

pause
