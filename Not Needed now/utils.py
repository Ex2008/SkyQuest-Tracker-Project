import pandas as pd
import numpy as np
import json
import logging
import time
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Cache:
    """Simple in-memory cache implementation"""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            # Check if cache entry is still valid (5 minutes)
            if time.time() - self._timestamps[key] < 300:
                return self._cache[key]
            else:
                # Remove expired entry
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self._timestamps.clear()
    
    def size(self) -> int:
        """Get cache size"""
        return len(self._cache)

# Global cache instance
cache = Cache()

def cache_result(timeout: int = 300):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            logger.debug(f"Cache miss for {func.__name__}, cached result")
            return result
        return wrapper
    return decorator

def create_response(data: Any, status: int = 200, message: str = "Success") -> Dict:
    """Create standardized API response"""
    return {
        "status": "success" if status < 400 else "error",
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
        "status_code": status
    }

def create_error_response(message: str, status: int = 400, errors: List[str] = None) -> Dict:
    """Create standardized error response"""
    return {
        "status": "error",
        "message": message,
        "errors": errors or [],
        "timestamp": datetime.utcnow().isoformat(),
        "status_code": status
    }

def log_api_request(request_data: Dict, response_data: Dict, duration: float) -> None:
    """Log API request and response for analytics"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "request": request_data,
        "response_status": response_data.get("status"),
        "duration_ms": round(duration * 1000, 2),
        "cache_hit": "cache_hit" in response_data
    }
    logger.info(f"API Request: {json.dumps(log_entry)}")

def calculate_similarity_score(event1: Dict, event2: Dict) -> float:
    """Calculate similarity score between two events"""
    score = 0.0
    
    # Event type similarity (weight: 0.4)
    if event1.get('event_type') == event2.get('event_type'):
        score += 0.4
    
    # Location similarity (weight: 0.3)
    if event1.get('location') == event2.get('location'):
        score += 0.3
    
    # Time of day similarity (weight: 0.2)
    if event1.get('time_of_day') == event2.get('time_of_day'):
        score += 0.2
    
    # Duration similarity (weight: 0.1)
    duration_diff = abs(event1.get('duration', 0) - event2.get('duration', 0))
    if duration_diff <= 60:  # Within 1 hour
        score += 0.1
    elif duration_diff <= 120:  # Within 2 hours
        score += 0.05
    
    return score

def filter_events_by_preferences(events_df: pd.DataFrame, preferences: Dict) -> pd.DataFrame:
    """Filter events based on user preferences"""
    filtered_df = events_df.copy()
    
    # Filter by event type
    if preferences.get('event_type'):
        filtered_df = filtered_df[
            filtered_df['event_type'].str.lower() == preferences['event_type'].lower()
        ]
    
    # Filter by location
    if preferences.get('location'):
        filtered_df = filtered_df[
            filtered_df['location'] == preferences['location']
        ]
    
    # Filter by time of day
    if preferences.get('time_of_day'):
        filtered_df = filtered_df[
            filtered_df['time_of_day'].str.lower() == preferences['time_of_day'].lower()
        ]
    
    return filtered_df

def rank_recommendations(recommendations: List[Dict], user_preferences: Dict) -> List[Dict]:
    """Rank recommendations based on user preferences and similarity"""
    for rec in recommendations:
        # Calculate similarity score
        similarity = calculate_similarity_score(rec, user_preferences)
        
        # Combine with like probability for final score
        like_prob = rec.get('like_probability', 0)
        final_score = (similarity * 0.6) + (like_prob * 0.4)
        
        rec['similarity_score'] = similarity
        rec['final_score'] = final_score
    
    # Sort by final score
    recommendations.sort(key=lambda x: x['final_score'], reverse=True)
    return recommendations

def validate_and_clean_preferences(preferences: Dict) -> tuple[Dict, List[str]]:
    """Validate and clean user preferences"""
    errors = []
    cleaned_prefs = {}
    
    # Required fields
    required_fields = ['event_type', 'location', 'time_of_day']
    for field in required_fields:
        if field not in preferences:
            errors.append(f"Missing required field: {field}")
        else:
            value = preferences[field]
            if not value or not isinstance(value, str):
                errors.append(f"Invalid {field}: must be a non-empty string")
            else:
                cleaned_prefs[field] = value.strip().lower()
    
    # Optional fields
    if 'min_popularity' in preferences:
        try:
            min_pop = float(preferences['min_popularity'])
            if 0 <= min_pop <= 10:
                cleaned_prefs['min_popularity'] = min_pop
            else:
                errors.append("min_popularity must be between 0 and 10")
        except ValueError:
            errors.append("min_popularity must be a number")
    
    if 'max_duration' in preferences:
        try:
            max_dur = int(preferences['max_duration'])
            if max_dur > 0:
                cleaned_prefs['max_duration'] = max_dur
            else:
                errors.append("max_duration must be positive")
        except ValueError:
            errors.append("max_duration must be an integer")
    
    return cleaned_prefs, errors

def generate_recommendation_explanation(recommendation: Dict, user_preferences: Dict) -> str:
    """Generate human-readable explanation for a recommendation"""
    reasons = []
    
    # Event type match
    if recommendation.get('event_type') == user_preferences.get('event_type'):
        reasons.append("matches your preferred event type")
    
    # Location match
    if recommendation.get('location') == user_preferences.get('location'):
        reasons.append("is in your preferred location")
    
    # Time of day match
    if recommendation.get('time_of_day') == user_preferences.get('time_of_day'):
        reasons.append("occurs at your preferred time")
    
    # High popularity
    if recommendation.get('popularity_score', 0) >= 8.0:
        reasons.append("is highly popular")
    elif recommendation.get('popularity_score', 0) >= 7.0:
        reasons.append("is quite popular")
    
    # High like probability
    if recommendation.get('like_probability', 0) >= 0.8:
        reasons.append("has a high chance you'll enjoy it")
    
    if reasons:
        return f"This event {' and '.join(reasons)}."
    else:
        return "This event might interest you based on general popularity."

def create_user_feedback_data(user_preferences: Dict, recommendations: List[Dict], 
                            selected_event: Dict, feedback: str) -> Dict:
    """Create structured feedback data for model improvement"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "user_preferences": user_preferences,
        "recommendations_shown": len(recommendations),
        "selected_event": selected_event,
        "feedback": feedback,
        "session_id": hashlib.md5(
            f"{user_preferences}{time.time()}".encode()
        ).hexdigest()[:8]
    }

def save_feedback_to_file(feedback_data: Dict, filename: str = "user_feedback.jsonl") -> None:
    """Save user feedback to a JSONL file for later analysis"""
    try:
        with open(filename, 'a') as f:
            f.write(json.dumps(feedback_data) + '\n')
        logger.info(f"Feedback saved: {feedback_data.get('session_id')}")
    except Exception as e:
        logger.error(f"Failed to save feedback: {e}")

def get_api_usage_stats() -> Dict:
    """Get API usage statistics"""
    return {
        "cache_size": cache.size(),
        "cache_hit_rate": 0.0,  # Would need to track hits/misses
        "total_requests": 0,    # Would need to track in production
        "average_response_time": 0.0,  # Would need to track in production
        "uptime": datetime.utcnow().isoformat()
    }

def format_duration(minutes: int) -> str:
    """Format duration in minutes to human-readable string"""
    if minutes < 60:
        return f"{minutes} minutes"
    elif minutes < 120:
        return f"{minutes//60} hour {minutes%60} minutes"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        return f"{hours} hours {remaining_minutes} minutes"

def enrich_event_data(event: Dict) -> Dict:
    """Add additional computed fields to event data"""
    enriched = event.copy()
    
    # Add formatted duration
    enriched['duration_formatted'] = format_duration(event.get('duration', 0))
    
    # Add popularity category
    popularity = event.get('popularity_score', 0)
    if popularity >= 9.0:
        enriched['popularity_category'] = 'Very Popular'
    elif popularity >= 8.0:
        enriched['popularity_category'] = 'Popular'
    elif popularity >= 7.0:
        enriched['popularity_category'] = 'Moderately Popular'
    else:
        enriched['popularity_category'] = 'Less Popular'
    
    # Add difficulty level (based on duration and type)
    duration = event.get('duration', 0)
    event_type = event.get('event_type', '').lower()
    
    if duration <= 60 or event_type in ['rocket launch']:
        enriched['difficulty'] = 'Easy'
    elif duration <= 180 or event_type in ['meteor shower', 'star party']:
        enriched['difficulty'] = 'Moderate'
    else:
        enriched['difficulty'] = 'Advanced'
    
    return enriched 