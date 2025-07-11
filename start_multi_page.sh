#!/bin/bash

echo "========================================"
echo "   SkyQuest Tracker - Multi-Page App"
echo "========================================"
echo

# Function to cleanup background processes
cleanup() {
    echo "Shutting down services..."
    kill $API_PID $WEB_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "Starting Backend API..."
python enhanced_app.py &
API_PID=$!

echo "Waiting for API to start..."
sleep 3

echo "Starting Web App..."
python web_app.py &
WEB_PID=$!

echo
echo "========================================"
echo "    Services Starting..."
echo "========================================"
echo
echo "Backend API: http://localhost:5000"
echo "Web App:     http://localhost:5001"
echo
echo "Pages Available:"
echo "  - Landing:      http://localhost:5001"
echo "  - Recommendations: http://localhost:5001/recommendations"
echo "  - Events:       http://localhost:5001/events"
echo "  - About:        http://localhost:5001/about"
echo

# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Opening landing page in browser..."
    open http://localhost:5001
elif command -v xdg-open &> /dev/null; then
    echo "Opening landing page in browser..."
    xdg-open http://localhost:5001
fi

echo
echo "Both services are now running!"
echo "Press Ctrl+C to stop all services."

# Wait for both processes
wait 