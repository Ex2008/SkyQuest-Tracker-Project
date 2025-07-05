from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pandas as pd
import numpy as np
import joblib
import os
import time
import logging
from datetime import datetime
from config import get_config, validate_user_preferences, VALID_EVENT_TYPES, VALID_LOCATIONS
from utils import (
    cache, cache_result, create_response, create_error_response, 
    log_api_request, filter_events_by_preferences, rank_recommendations,
    validate_and_clean_preferences, generate_recommendation_explanation,
    create_user_feedback_data, save_feedback_to_file, get_api_usage_stats,
    enrich_event_data
)

# Initialize Flask app
app = Flask(__name__)
config = get_config()
app.config.from_object(config)
config.init_app(app)

# Enable CORS
CORS(app, origins=config.CORS_ORIGINS)

# Set up rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[f"{config.RATE_LIMIT} per minute"]
)

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Global variables to store the model and data
model = None
events_data = None

def load_model():
    """Load the trained model and events data"""
    global model, events_data
    
    try:
        if not os.path.exists(config.MODEL_PATH):
            raise FileNotFoundError(f"Model file not found: {config.MODEL_PATH}")
        
        if not os.path.exists(config.DATA_PATH):
            raise FileNotFoundError(f"Data file not found: {config.DATA_PATH}")
        
        model = joblib.load(config.MODEL_PATH)
        events_data = joblib.load(config.DATA_PATH)
        
        logger.info("Model and data loaded successfully!")
        logger.info(f"Loaded {len(events_data)} events")
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

@app.before_request
def before_request():
    """Log request details"""
    request.start_time = time.time()
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def after_request(response):
    """Log response details and add headers"""
    duration = time.time() - request.start_time
    
    # Add response headers
    response.headers['X-Response-Time'] = str(duration)
    response.headers['X-API-Version'] = 'v1'
    
    # Log request/response
    try:
        request_data = request.get_json() if request.is_json else {}
        response_data = response.get_json() if response.is_json else {}
        log_api_request(request_data, response_data, duration)
    except Exception as e:
        logger.warning(f"Could not log request/response: {e}")
    
    return response

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return create_error_response("Endpoint not found", 404)

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return create_error_response("Internal server error", 500)

@app.errorhandler(429)
def ratelimit_handler(error):
    """Handle rate limit errors"""
    return create_error_response("Rate limit exceeded", 429)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return create_response({
        "status": "healthy",
        "model_loaded": model is not None,
        "events_count": len(events_data) if events_data is not None else 0,
        "cache_size": cache.size(),
        "uptime": datetime.utcnow().isoformat()
    })

@app.route('/events', methods=['GET'])
@limiter.limit("100 per minute")
@cache_result(timeout=300)
def get_all_events():
    """Get all available events with optional filtering"""
    try:
        if events_data is None:
            return create_error_response("Events data not loaded", 500)
        
        # Get query parameters
        event_type = request.args.get('event_type')
        location = request.args.get('location')
        time_of_day = request.args.get('time_of_day')
        min_popularity = request.args.get('min_popularity', type=float)
        max_duration = request.args.get('max_duration', type=int)
        
        # Filter events
        filtered_events = events_data.copy()
        
        if event_type:
            filtered_events = filtered_events[
                filtered_events['event_type'].str.lower() == event_type.lower()
            ]
        
        if location:
            filtered_events = filtered_events[filtered_events['location'] == location]
        
        if time_of_day:
            filtered_events = filtered_events[
                filtered_events['time_of_day'].str.lower() == time_of_day.lower()
            ]
        
        if min_popularity is not None:
            filtered_events = filtered_events[
                filtered_events['popularity_score'] >= min_popularity
            ]
        
        if max_duration is not None:
            filtered_events = filtered_events[
                filtered_events['duration'] <= max_duration
            ]
        
        # Enrich event data
        events_list = []
        for _, event in filtered_events.iterrows():
            enriched_event = enrich_event_data(event.to_dict())
            events_list.append(enriched_event)
        
        return create_response({
            "total_events": len(events_list),
            "events": events_list,
            "filters_applied": {
                "event_type": event_type,
                "location": location,
                "time_of_day": time_of_day,
                "min_popularity": min_popularity,
                "max_duration": max_duration
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return create_error_response("Error retrieving events", 500)

@app.route('/recommend', methods=['POST'])
@limiter.limit("50 per minute")
def recommend_events():
    """Recommend top 3 space events based on user preferences"""
    start_time = time.time()
    
    try:
        # Get and validate user preferences
        user_prefs = request.get_json()
        
        if not user_prefs:
            return create_error_response("No data provided", 400)
        
        # Validate and clean preferences
        cleaned_prefs, validation_errors = validate_and_clean_preferences(user_prefs)
        
        if validation_errors:
            return create_error_response(
                "Invalid input data", 
                400, 
                errors=validation_errors
            )
        
        # Create recommendation data with various combinations
        user_data = []
        durations = [60, 120, 180, 240, 300]
        popularity_scores = [7.0, 7.5, 8.0, 8.5, 9.0]
        
        for duration in durations:
            for popularity in popularity_scores:
                user_data.append({
                    'event_type': cleaned_prefs['event_type'],
                    'location': cleaned_prefs['location'],
                    'time_of_day': cleaned_prefs['time_of_day'],
                    'duration': duration,
                    'popularity_score': popularity
                })
        
        user_df = pd.DataFrame(user_data)
        
        # Get predictions
        predictions = model.predict(user_df)
        prediction_probs = model.predict_proba(user_df)
        like_probabilities = prediction_probs[:, 1]
        
        # Add predictions to user data
        user_df['predicted_like'] = predictions
        user_df['like_probability'] = like_probabilities
        
        # Filter liked events and get top recommendations
        liked_events = user_df[user_df['predicted_like'] == 1]
        
        if len(liked_events) == 0:
            # Fallback to popular events
            top_events = events_data.nlargest(config.MAX_RECOMMENDATIONS, 'popularity_score')
            recommendations = []
            
            for _, event in top_events.iterrows():
                enriched_event = enrich_event_data(event.to_dict())
                enriched_event.update({
                    'predicted_like': 0,
                    'like_probability': 0.0,
                    'reason': 'No specific matches found, showing popular events'
                })
                recommendations.append(enriched_event)
        else:
            # Get top recommendations
            top_liked = liked_events.nlargest(config.MAX_RECOMMENDATIONS, 'like_probability')
            recommendations = []
            
            for _, event in top_liked.iterrows():
                enriched_event = enrich_event_data(event.to_dict())
                enriched_event.update({
                    'predicted_like': int(event['predicted_like']),
                    'like_probability': float(event['like_probability']),
                    'reason': generate_recommendation_explanation(enriched_event, cleaned_prefs)
                })
                recommendations.append(enriched_event)
        
        # Rank recommendations
        recommendations = rank_recommendations(recommendations, cleaned_prefs)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        return create_response({
            "user_preferences": cleaned_prefs,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "response_time_ms": round(response_time * 1000, 2),
            "cache_hit": False  # Would be True if using cache decorator
        })
        
    except Exception as e:
        logger.error(f"Error in recommendation: {e}")
        return create_error_response("Error generating recommendations", 500)

@app.route('/feedback', methods=['POST'])
@limiter.limit("20 per minute")
def submit_feedback():
    """Submit user feedback on recommendations"""
    try:
        feedback_data = request.get_json()
        
        if not feedback_data:
            return create_error_response("No feedback data provided", 400)
        
        required_fields = ['user_preferences', 'selected_event', 'feedback']
        for field in required_fields:
            if field not in feedback_data:
                return create_error_response(f"Missing required field: {field}", 400)
        
        # Create structured feedback
        structured_feedback = create_user_feedback_data(
            feedback_data['user_preferences'],
            feedback_data.get('recommendations_shown', []),
            feedback_data['selected_event'],
            feedback_data['feedback']
        )
        
        # Save feedback
        save_feedback_to_file(structured_feedback)
        
        return create_response({
            "message": "Feedback submitted successfully",
            "session_id": structured_feedback['session_id']
        })
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return create_error_response("Error submitting feedback", 500)

@app.route('/stats', methods=['GET'])
@limiter.limit("10 per minute")
def get_stats():
    """Get API usage statistics"""
    try:
        stats = get_api_usage_stats()
        
        # Add model statistics
        if events_data is not None:
            stats.update({
                "total_events": len(events_data),
                "event_types": events_data['event_type'].nunique(),
                "locations": events_data['location'].nunique(),
                "avg_popularity": float(events_data['popularity_score'].mean()),
                "avg_duration": float(events_data['duration'].mean())
            })
        
        return create_response(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return create_error_response("Error retrieving statistics", 500)

@app.route('/validate', methods=['POST'])
def validate_preferences():
    """Validate user preferences without making recommendations"""
    try:
        user_prefs = request.get_json()
        
        if not user_prefs:
            return create_error_response("No data provided", 400)
        
        # Validate preferences
        validation_errors = validate_user_preferences(user_prefs)
        
        if validation_errors:
            return create_response({
                "valid": False,
                "errors": validation_errors
            })
        else:
            return create_response({
                "valid": True,
                "message": "Preferences are valid"
            })
        
    except Exception as e:
        logger.error(f"Error validating preferences: {e}")
        return create_error_response("Error validating preferences", 500)

@app.route('/event-types', methods=['GET'])
@cache_result(timeout=3600)  # Cache for 1 hour
def get_event_types():
    """Get all available event types"""
    try:
        if events_data is None:
            return create_error_response("Events data not loaded", 500)
        
        event_types = events_data['event_type'].unique().tolist()
        event_types.sort()
        
        return create_response({
            "event_types": event_types,
            "count": len(event_types)
        })
        
    except Exception as e:
        logger.error(f"Error getting event types: {e}")
        return create_error_response("Error retrieving event types", 500)

@app.route('/locations', methods=['GET'])
@cache_result(timeout=3600)  # Cache for 1 hour
def get_locations():
    """Get all available locations"""
    try:
        if events_data is None:
            return create_error_response("Events data not loaded", 500)
        
        locations = events_data['location'].unique().tolist()
        locations.sort()
        
        return create_response({
            "locations": locations,
            "count": len(locations)
        })
        
    except Exception as e:
        logger.error(f"Error getting locations: {e}")
        return create_error_response("Error retrieving locations", 500)

if __name__ == '__main__':
    # Load the model when starting the app
    try:
        load_model()
        logger.info("Starting enhanced Flask API server...")
        app.run(debug=config.DEBUG, host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        logger.error("Please make sure to run train_model.py first to create the model files.") 