@echo off
echo ========================================
echo    SkyQuest Tracker - Web App Only
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo Checking required packages...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r web_requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install packages
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Starting SkyQuest Tracker Web App...
echo.
echo The web app will run in standalone mode with sample data.
echo To enable full functionality, also start the backend API.
echo.

python web_app.py

echo.
echo Web app stopped.
pause 