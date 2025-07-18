#!/bin/bash

echo "========================================"
echo "   SkyQuest Tracker - Web App Only"
echo "========================================"
echo

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

echo "Checking required packages..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "Installing required packages..."
    pip3 install -r web_requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install packages"
        exit 1
    fi
fi

echo
echo "🚀 Starting SkyQuest Tracker Web App..."
echo
echo "The web app will run in standalone mode with sample data."
echo "To enable full functionality, also start the backend API."
echo

python3 web_app.py

echo
echo "Web app stopped." 