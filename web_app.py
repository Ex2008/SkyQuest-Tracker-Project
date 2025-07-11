from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import requests
import os
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# API configuration
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:5000/api/v1')
API_AVAILABLE = False

class APIError(Exception):
    """Custom exception for API errors"""
    pass

def check_api_availability():
    """Check if the backend API is available"""
    global API_AVAILABLE
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        API_AVAILABLE = response.status_code == 200
        return API_AVAILABLE
    except:
        API_AVAILABLE = False
        return False

def call_api(endpoint, method='GET', data=None):
    """Make API calls to the backend"""
    if not API_AVAILABLE:
        raise APIError("Backend API is not available")
    
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise APIError(f"API request failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise APIError(f"Unexpected error: {str(e)}")

@app.route('/')
def landing():
    """Landing page"""
    return render_template('landing.html')

@app.route('/recommendations')
def recommendations():
    """Recommendations page"""
    return render_template('recommendations.html')

@app.route('/events')
def events():
    """Events page"""
    return render_template('events.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        if API_AVAILABLE:
            api_response = call_api('/health')
            return jsonify({
                'status': 'healthy',
                'api_status': api_response.get('status', 'unknown'),
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'status': 'healthy',
                'api_status': 'unavailable',
                'timestamp': datetime.utcnow().isoformat()
            })
    except APIError as e:
        return jsonify({
            'status': 'healthy',
            'api_status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        })

@app.route('/api/events')
def api_events():
    """Proxy for events API"""
    if not API_AVAILABLE:
        # Return sample data when API is not available
        return jsonify({
            "total_events": 3,
            "events": [
                {
                    "id": 1,
                    "event_type": "meteor_shower",
                    "name": "Perseid Meteor Shower",
                    "date": "2024-08-12",
                    "location": "Northern Hemisphere",
                    "duration": 180,
                    "popularity_score": 9.0,
                    "description": "One of the most spectacular meteor showers of the year"
                },
                {
                    "id": 2,
                    "event_type": "solar_eclipse",
                    "name": "Total Solar Eclipse",
                    "date": "2024-10-14",
                    "location": "North America",
                    "duration": 240,
                    "popularity_score": 9.5,
                    "description": "A rare total solar eclipse visible across North America"
                },
                {
                    "id": 3,
                    "event_type": "rocket_launch",
                    "name": "SpaceX Falcon 9 Launch",
                    "date": "2024-09-15",
                    "location": "Kennedy Space Center",
                    "duration": 120,
                    "popularity_score": 8.0,
                    "description": "Commercial satellite launch mission"
                }
            ]
        })
    
    try:
        # Get query parameters
        event_type = request.args.get('event_type')
        timeframe = request.args.get('timeframe')
        location = request.args.get('location')
        sort_by = request.args.get('sort_by', 'date')
        
        # Build query parameters
        params = {}
        if event_type:
            params['event_type'] = event_type
        if timeframe:
            params['timeframe'] = timeframe
        if location:
            params['location'] = location
        if sort_by:
            params['sort_by'] = sort_by
        
        # Make request to backend API
        response = requests.get(f"{API_BASE_URL}/events", params=params, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to load events"}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API connection error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    """Proxy for recommendation API"""
    if not API_AVAILABLE:
        # Return sample recommendations when API is not available
        return jsonify({
            "user_preferences": request.get_json(),
            "recommendations": [
                {
                    "event_type": "meteor_shower",
                    "location": "Northern Hemisphere",
                    "time_of_day": "night",
                    "duration": 180,
                    "popularity_score": 9.0,
                    "predicted_like": 1,
                    "like_probability": 0.95,
                    "reason": "Based on your preferences"
                },
                {
                    "event_type": "solar_eclipse",
                    "location": "North America",
                    "time_of_day": "day",
                    "duration": 240,
                    "popularity_score": 9.5,
                    "predicted_like": 1,
                    "like_probability": 0.92,
                    "reason": "Based on your preferences"
                }
            ],
            "total_recommendations": 2
        })
    
    try:
        data = request.get_json()
        
        # Make request to backend API
        response = requests.post(f"{API_BASE_URL}/recommend", json=data, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to get recommendations"}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API connection error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/event/<event_id>')
def api_event_details(event_id):
    """Proxy for event details API"""
    try:
        response = requests.get(f"{API_BASE_URL}/event/{event_id}", timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Event not found"}), 404
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API connection error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/event-types')
def api_event_types():
    """Proxy for event types API"""
    try:
        response = requests.get(f"{API_BASE_URL}/event-types", timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to load event types"}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API connection error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/locations')
def api_locations():
    """Proxy for locations API"""
    try:
        response = requests.get(f"{API_BASE_URL}/locations", timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to load locations"}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API connection error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/feedback', methods=['POST'])
def api_feedback():
    """Proxy for feedback API"""
    try:
        data = request.get_json()
        response = requests.post(f"{API_BASE_URL}/feedback", json=data, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to submit feedback"}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API connection error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/stats')
def api_stats():
    """Proxy for stats API"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to load statistics"}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API connection error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return render_template('500.html'), 500

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

# Admin routes (for future use)
@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    try:
        stats = call_api('/stats')
        return render_template('admin/dashboard.html', stats=stats)
    except APIError as e:
        return render_template('admin/dashboard.html', stats=None, error=str(e))

@app.route('/admin/feedback')
def admin_feedback():
    """Admin feedback page"""
    return render_template('admin/feedback.html')

# Development routes for testing
@app.route('/test')
def test_page():
    """Test page for development"""
    return """
    <h1>SkyQuest Tracker - Test Page</h1>
    <p>All systems operational!</p>
    <ul>
        <li><a href="/">Landing Page</a></li>
        <li><a href="/recommendations">Recommendations</a></li>
        <li><a href="/events">Events</a></li>
        <li><a href="/about">About</a></li>
        <li><a href="/health">Health Check</a></li>
    </ul>
    """

if __name__ == '__main__':
    # Check if backend API is running
    print("🔍 Checking backend API availability...")
    if check_api_availability():
        print("✅ Backend API is running and accessible")
    else:
        print("⚠️  Backend API is not accessible. Running in standalone mode with sample data.")
        print("   To enable full functionality, start the backend API with: python enhanced_app.py")
    
    print("🚀 Starting SkyQuest Tracker Web App...")
    print("   Landing page: http://localhost:5001")
    print("   Recommendations: http://localhost:5001/recommendations")
    print("   Events: http://localhost:5001/events")
    print("   About: http://localhost:5001/about")
    print("   Health check: http://localhost:5001/health")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 