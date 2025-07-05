@echo off
REM Space Events API Startup Script for Windows
echo 🚀 Starting Space Events API...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed. Please install pip first.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if model files exist
if not exist "space_events_model.pkl" (
    echo 🤖 Training machine learning model...
    python train_model.py
    
    if errorlevel 1 (
        echo ❌ Model training failed. Please check the error messages above.
        pause
        exit /b 1
    )
    echo ✅ Model training completed successfully!
) else (
    echo ✅ Model files already exist, skipping training.
)

REM Run tests if test file exists
if exist "test_api.py" (
    echo 🧪 Running API tests...
    python test_api.py
    
    if errorlevel 1 (
        echo ⚠️  Some tests failed, but continuing with startup...
    ) else (
        echo ✅ All tests passed!
    )
)

REM Start the API server
echo 🌐 Starting Flask API server...
echo 📡 API will be available at: http://localhost:5000
echo 📊 Health check: http://localhost:5000/health
echo 📚 API documentation: Check README.md
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the enhanced Flask app
python enhanced_app.py

pause 