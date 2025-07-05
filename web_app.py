from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import requests
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# API configuration
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:5000/api/v1')

class APIError(Exception):
    """Custom exception for API errors"""
    pass

def call_api(endpoint, method='GET', data=None):
    """Make API calls to the backend"""
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
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        api_response = call_api('/health')
        return jsonify({
            'status': 'healthy',
            'api_status': api_response.get('status', 'unknown'),
            'timestamp': datetime.utcnow().isoformat()
        })
    except APIError as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@app.route('/api/events')
def get_events():
    """Get all events with optional filtering"""
    try:
        # Get query parameters
        event_type = request.args.get('event_type')
        location = request.args.get('location')
        time_of_day = request.args.get('time_of_day')
        min_popularity = request.args.get('min_popularity', type=float)
        max_duration = request.args.get('max_duration', type=int)
        
        # Build API URL with filters
        params = {}
        if event_type:
            params['event_type'] = event_type
        if location:
            params['location'] = location
        if time_of_day:
            params['time_of_day'] = time_of_day
        if min_popularity:
            params['min_popularity'] = min_popularity
        if max_duration:
            params['max_duration'] = max_duration
        
        endpoint = '/events'
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            endpoint += f"?{query_string}"
        
        api_response = call_api(endpoint)
        return jsonify(api_response)
    
    except APIError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommend', methods=['POST'])
def recommend_events():
    """Get event recommendations"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        api_response = call_api('/recommend', method='POST', data=data)
        return jsonify(api_response)
    
    except APIError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/event-types')
def get_event_types():
    """Get all event types"""
    try:
        api_response = call_api('/event-types')
        return jsonify(api_response)
    except APIError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/locations')
def get_locations():
    """Get all locations"""
    try:
        api_response = call_api('/locations')
        return jsonify(api_response)
    except APIError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No feedback data provided'}), 400
        
        api_response = call_api('/feedback', method='POST', data=data)
        return jsonify(api_response)
    
    except APIError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get API statistics"""
    try:
        api_response = call_api('/stats')
        return jsonify(api_response)
    except APIError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate', methods=['POST'])
def validate_preferences():
    """Validate user preferences"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        api_response = call_api('/validate', method='POST', data=data)
        return jsonify(api_response)
    
    except APIError as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return render_template('500.html'), 500

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/events')
def events_page():
    """Events page"""
    return render_template('events.html')

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

if __name__ == '__main__':
    # Check if API is available
    try:
        call_api('/health')
        logger.info("API is available")
    except APIError as e:
        logger.warning(f"API is not available: {e}")
        logger.warning("Make sure the API server is running on http://localhost:5000")
    
    # Start the web server
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting web server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug) 