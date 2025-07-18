#!/bin/bash

# Space Events API Startup Script
echo "🚀 Starting Space Events API..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if model files exist
if [ ! -f "space_events_model.pkl" ] || [ ! -f "events_data.pkl" ]; then
    echo "🤖 Training machine learning model..."
    python train_model.py
    
    if [ $? -ne 0 ]; then
        echo "❌ Model training failed. Please check the error messages above."
        exit 1
    fi
    echo "✅ Model training completed successfully!"
else
    echo "✅ Model files already exist, skipping training."
fi

# Run tests if test file exists
if [ -f "test_api.py" ]; then
    echo "🧪 Running API tests..."
    python test_api.py
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Some tests failed, but continuing with startup..."
    else
        echo "✅ All tests passed!"
    fi
fi

# Start the API server
echo "🌐 Starting Flask API server..."
echo "📡 API will be available at: http://localhost:5000"
echo "📊 Health check: http://localhost:5000/health"
echo "📚 API documentation: Check README.md"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the enhanced Flask app
python enhanced_app.py 