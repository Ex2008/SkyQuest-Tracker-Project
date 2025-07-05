from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os

app = Flask(__name__)

# Global variables to store the model and data
model = None
events_data = None

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

@app.route('/recommend', methods=['POST'])
def recommend_events():
    """
    Recommend top 3 space events based on user preferences
    
    Expected input format:
    {
        "event_type": "meteor shower",
        "location": "USA", 
        "time_of_day": "night"
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
        
        if len(liked_events) == 0:
            # If no events are predicted to be liked, return top events by popularity
            top_events = events_data.nlargest(3, 'popularity_score')
            recommendations = []
            
            for _, event in top_events.iterrows():
                recommendations.append({
                    'event_type': event['event_type'],
                    'location': event['location'],
                    'time_of_day': event['time_of_day'],
                    'duration': int(event['duration']),
                    'popularity_score': float(event['popularity_score']),
                    'predicted_like': 0,
                    'like_probability': 0.0,
                    'reason': 'No specific matches found, showing popular events'
                })
        else:
            # Sort by like probability and get top 3
            top_liked = liked_events.nlargest(3, 'like_probability')
            recommendations = []
            
            for _, event in top_liked.iterrows():
                recommendations.append({
                    'event_type': event['event_type'],
                    'location': event['location'],
                    'time_of_day': event['time_of_day'],
                    'duration': int(event['duration']),
                    'popularity_score': float(event['popularity_score']),
                    'predicted_like': int(event['predicted_like']),
                    'like_probability': float(event['like_probability']),
                    'reason': 'Based on your preferences'
                })
        
        return jsonify({
            "user_preferences": user_prefs,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "model_loaded": model is not None})

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

if __name__ == '__main__':
    # Load the model when starting the app
    try:
        load_model()
        print("Starting Flask API server...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Please make sure to run train_model.py first to create the model files.") 