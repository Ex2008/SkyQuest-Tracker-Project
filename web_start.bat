@echo off
echo ========================================
echo SkyQuest Tracker - Web Application
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install web requirements
echo Installing web application dependencies...
pip install -r web_requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Check if API server is running
echo Checking API server status...
curl -s http://localhost:5000/api/v1/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: API server is not running on http://localhost:5000
    echo Please start the API server first using start.bat
    echo.
    echo Starting web application anyway (some features may not work)...
    echo.
) else (
    echo API server is running
    echo.
)

REM Set environment variables
set FLASK_APP=web_app.py
set FLASK_ENV=development
set PORT=8000

echo Starting web application on http://localhost:%PORT%...
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the web application
python web_app.py

REM Deactivate virtual environment on exit
call venv\Scripts\deactivate.bat
echo.
echo Web application stopped.
pause 