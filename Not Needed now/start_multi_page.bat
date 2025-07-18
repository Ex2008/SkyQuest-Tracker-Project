@echo off
echo ========================================
echo    SkyQuest Tracker - Multi-Page App
echo ========================================
echo.

echo Starting Backend API...
start "SkyQuest API" cmd /k "python enhanced_app.py"

echo Waiting for API to start...
timeout /t 3 /nobreak > nul

echo Starting Web App...
start "SkyQuest Web" cmd /k "python web_app.py"

echo.
echo ========================================
echo    Services Starting...
echo ========================================
echo.
echo Backend API: http://localhost:5000
echo Web App:     http://localhost:5001
echo.
echo Pages Available:
echo   - Landing:      http://localhost:5001
echo   - Recommendations: http://localhost:5001/recommendations
echo   - Events:       http://localhost:5001/events
echo   - About:        http://localhost:5001/about
echo.
echo Press any key to open the landing page...
pause > nul

start http://localhost:5001

echo.
echo Both services are now running!
echo Close the command windows to stop the services.
pause 