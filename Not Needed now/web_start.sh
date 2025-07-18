#!/bin/bash

echo "========================================"
echo "SkyQuest Tracker - Web Application"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

echo "Python found:"
python3 --version
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Install/upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install web requirements
echo "Installing web application dependencies..."
pip install -r web_requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Check if API server is running
echo "Checking API server status..."
if curl -s http://localhost:5000/api/v1/health > /dev/null 2>&1; then
    echo "API server is running"
    echo
else
    echo "WARNING: API server is not running on http://localhost:5000"
    echo "Please start the API server first using ./start.sh"
    echo
    echo "Starting web application anyway (some features may not work)..."
    echo
fi

# Set environment variables
export FLASK_APP=web_app.py
export FLASK_ENV=development
export PORT=8000

echo "Starting web application on http://localhost:$PORT..."
echo
echo "Press Ctrl+C to stop the server"
echo

# Start the web application
python web_app.py

# Deactivate virtual environment on exit
deactivate
echo
echo "Web application stopped." 