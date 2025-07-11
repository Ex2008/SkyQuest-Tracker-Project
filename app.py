from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os
import requests
import json
from datetime import datetime, timedelta
import time

app = Flask(__name__)

# Global variables to store the model and data
model = None
events_data = None

# NASA API configuration
NASA_API_BASE_URL = "https://api.nasa.gov"
NASA_API_KEY = os.getenv('NASA_API_KEY', 'DEMO_KEY')  # Use DEMO_KEY as fallback

def load_model():
    """Load the trained model and events data"""
    global model, events_data
    
    if not os.path.exists('space_events_model.pkl'):
        raise FileNotFoundError("Model file not found. Please run train_model.py first.")
    
    if not os.path.exists('events_data.pkl'):
        raise FileNotFoundError("Events data file not found. Please run train_model.py first.")
    
    model = joblib.load('space_events_model.pkl')
    events_data = joblib.load('events_data.pkl')
    print("Model and data loaded successfully!")

def get_nasa_apod():
    """Get NASA's Astronomy Picture of the Day"""
    try:
        url = f"{NASA_API_BASE_URL}/planetary/apod"
        params = {
            'api_key': NASA_API_KEY,
            'count': 1
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching NASA APOD: {e}")
        return None

def get_nasa_asteroids():
    """Get near-Earth asteroid data from NASA"""
    try:
        # Get asteroids for today
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"{NASA_API_BASE_URL}/neo/rest/v1/feed"
        params = {
            'api_key': NASA_API_KEY,
            'start_date': today,
            'end_date': today
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching NASA asteroids: {e}")
        return None

def get_nasa_events():
    """Get space events from NASA API"""
    nasa_events = []
    
    # Get APOD
    apod_data = get_nasa_apod()
    if apod_data and len(apod_data) > 0:
        apod = apod_data[0]
        nasa_events.append({
            'event_type': 'nasa_apod',
            'title': apod.get('title', 'Astronomy Picture of the Day'),
            'description': apod.get('explanation', 'Daily space image from NASA'),
            'date': apod.get('date', datetime.now().strftime('%Y-%m-%d')),
            'image_url': apod.get('url', ''),
            'source': 'NASA APOD',
            'popularity_score': 9.0,
            'duration': 60,
            'time_of_day': 'any',
            'location': 'Global'
        })
    
    # Get asteroid data
    asteroid_data = get_nasa_asteroids()
    if asteroid_data and 'near_earth_objects' in asteroid_data:
        today = datetime.now().strftime('%Y-%m-%d')
        if today in asteroid_data['near_earth_objects']:
            asteroids = asteroid_data['near_earth_objects'][today]
            for asteroid in asteroids[:3]:  # Limit to 3 asteroids
                nasa_events.append({
                    'event_type': 'near_earth_asteroid',
                    'title': f"Asteroid {asteroid.get('name', 'Unknown')}",
                    'description': f"Near-Earth asteroid passing by today",
                    'date': today,
                    'distance_km': asteroid.get('close_approach_data', [{}])[0].get('miss_distance', {}).get('kilometers', 'Unknown'),
                    'velocity_kmh': asteroid.get('close_approach_data', [{}])[0].get('relative_velocity', {}).get('kilometers_per_hour', 'Unknown'),
                    'source': 'NASA NEO',
                    'popularity_score': 8.5,
                    'duration': 120,
                    'time_of_day': 'night',
                    'location': 'Global'
                })
    
    return nasa_events

@app.route('/recommend', methods=['POST'])
def recommend_events():
    """
    Recommend top 3 space events based on user preferences
    
    Expected input format:
    {
        "event_type": "meteor shower",
        "location": "USA", 
        "time_of_day": "night",
        "include_nasa": true
    }
    """
    try:
        # Get user preferences from request
        user_prefs = request.get_json()
        
        if not user_prefs:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['event_type', 'location', 'time_of_day']
        for field in required_fields:
            if field not in user_prefs:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if NASA events should be included
        include_nasa = user_prefs.get('include_nasa', True)
        
        # Get NASA events if requested
        nasa_events = []
        if include_nasa:
            nasa_events = get_nasa_events()
        
        # Create a DataFrame with user preferences
        # We'll create multiple rows with different duration and popularity scores
        # to get a variety of recommendations
        user_data = []
        
        # Generate different combinations of duration and popularity for variety
        durations = [60, 120, 180, 240, 300]
        popularity_scores = [7.0, 7.5, 8.0, 8.5, 9.0]
        
        for duration in durations:
            for popularity in popularity_scores:
                user_data.append({
                    'event_type': user_prefs['event_type'],
                    'location': user_prefs['location'],
                    'time_of_day': user_prefs['time_of_day'],
                    'duration': duration,
                    'popularity_score': popularity
                })
        
        user_df = pd.DataFrame(user_data)
        
        # Get predictions for all combinations
        predictions = model.predict(user_df)
        prediction_probs = model.predict_proba(user_df)
        
        # Get the probability of liking (class 1)
        like_probabilities = prediction_probs[:, 1]
        
        # Add predictions and probabilities to the user data
        user_df['predicted_like'] = predictions
        user_df['like_probability'] = like_probabilities
        
        # Filter events that are predicted to be liked
        liked_events = user_df[user_df['predicted_like'] == 1]
        
        recommendations = []
        
        if len(liked_events) == 0:
            # If no events are predicted to be liked, return top events by popularity
            top_events = events_data.nlargest(3, 'popularity_score')
            
            for _, event in top_events.iterrows():
                recommendations.append({
                    'event_type': event['event_type'],
                    'location': event['location'],
                    'time_of_day': event['time_of_day'],
                    'duration': int(event['duration']),
                    'popularity_score': float(event['popularity_score']),
                    'predicted_like': 0,
                    'like_probability': 0.0,
                    'reason': 'No specific matches found, showing popular events',
                    'source': 'Trained Model'
                })
        else:
            # Sort by like probability and get top 3
            top_liked = liked_events.nlargest(3, 'like_probability')
            
            for _, event in top_liked.iterrows():
                recommendations.append({
                    'event_type': event['event_type'],
                    'location': event['location'],
                    'time_of_day': event['time_of_day'],
                    'duration': int(event['duration']),
                    'popularity_score': float(event['popularity_score']),
                    'predicted_like': int(event['predicted_like']),
                    'like_probability': float(event['like_probability']),
                    'reason': 'Based on your preferences',
                    'source': 'Trained Model'
                })
        
        # Add NASA events to recommendations if available
        if nasa_events:
            for nasa_event in nasa_events[:2]:  # Add up to 2 NASA events
                recommendations.append({
                    'event_type': nasa_event['event_type'],
                    'location': nasa_event['location'],
                    'time_of_day': nasa_event['time_of_day'],
                    'duration': nasa_event['duration'],
                    'popularity_score': nasa_event['popularity_score'],
                    'predicted_like': 1,
                    'like_probability': 0.9,
                    'reason': 'Live NASA data',
                    'source': nasa_event['source'],
                    'title': nasa_event.get('title', ''),
                    'description': nasa_event.get('description', ''),
                    'date': nasa_event.get('date', ''),
                    'image_url': nasa_event.get('image_url', ''),
                    'distance_km': nasa_event.get('distance_km', ''),
                    'velocity_kmh': nasa_event.get('velocity_kmh', '')
                })
        
        # Limit to top 3 recommendations
        recommendations = recommendations[:3]
        
        return jsonify({
            "user_preferences": user_prefs,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "nasa_events_included": len([r for r in recommendations if r.get('source', '').startswith('NASA')]),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/nasa/events', methods=['GET'])
def get_nasa_events_endpoint():
    """Get live NASA space events"""
    try:
        nasa_events = get_nasa_events()
        return jsonify({
            "events": nasa_events,
            "total_events": len(nasa_events),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "model_loaded": model is not None,
        "nasa_api_key": "configured" if NASA_API_KEY != 'DEMO_KEY' else "using_demo_key"
    })

@app.route('/events', methods=['GET'])
def get_all_events():
    """Get all available events"""
    if events_data is None:
        return jsonify({"error": "Events data not loaded"}), 500
    
    events_list = events_data.to_dict('records')
    return jsonify({
        "total_events": len(events_list),
        "events": events_list
    })

@app.route('/model/info', methods=['GET'])
def get_model_info():
    """Get information about the trained model"""
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        # Get feature names if available
        feature_names = []
        if hasattr(model, 'named_steps') and 'preprocessor' in model.named_steps:
            preprocessor = model.named_steps['preprocessor']
            if hasattr(preprocessor, 'named_transformers_'):
                cat_features = preprocessor.named_transformers_.get('cat')
                if cat_features and hasattr(cat_features, 'get_feature_names_out'):
                    feature_names = cat_features.get_feature_names_out().tolist()
        
        return jsonify({
            "model_type": "DecisionTreeClassifier",
            "feature_names": feature_names,
            "training_data_size": len(events_data) if events_data is not None else 0,
            "available_event_types": events_data['event_type'].unique().tolist() if events_data is not None else [],
            "available_locations": events_data['location'].unique().tolist() if events_data is not None else []
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Load the model when starting the app
    try:
        load_model()
        print("Starting Flask API server...")
        print(f"NASA API Key: {'Configured' if NASA_API_KEY != 'DEMO_KEY' else 'Using DEMO_KEY'}")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Please make sure to run train_model.py first to create the model files.") 