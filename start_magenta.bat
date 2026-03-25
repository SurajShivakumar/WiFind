@echo off
REM Quick Start Script for Magenta AI Chatbot

echo ================================================================
echo          MAGENTA AI - WiFi Signal Analyzer
echo          Choose Your Experience!
echo ================================================================
echo.
echo What would you like to do?
echo.
echo [1] Start Automatic Monitoring (with friendly AI updates)
echo [2] Start Interactive Chat Mode (chat with Magenta!)
echo [3] Exit
echo.
echo ================================================================

choice /C 123 /N /M "Enter your choice (1, 2, or 3): "

if errorlevel 3 goto :end
if errorlevel 2 goto :interactive
if errorlevel 1 goto :automatic

:automatic
echo.
echo Starting Automatic Monitoring Mode...
echo Magenta will provide friendly updates every 5 seconds
echo Press Ctrl+C to stop
echo.
python signal_analyzer_bot.py
goto :end

:interactive
echo.
echo Starting Interactive Chat Mode...
echo You can chat with Magenta in real-time!
echo.
python signal_analyzer_bot_interactive.py
goto :end

:end
echo.
echo Thanks for using Magenta! 🤖
pause
