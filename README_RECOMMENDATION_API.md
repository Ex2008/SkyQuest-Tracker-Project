# Space Events Recommendation API

A Flask-based API that provides personalized space event recommendations using machine learning and live NASA data.

## Features

- **Machine Learning Recommendations**: Uses DecisionTreeClassifier trained on space events data
- **NASA API Integration**: Includes live data from NASA's Astronomy Picture of the Day and Near-Earth Object APIs
- **Personalized Suggestions**: Recommends events based on user preferences
- **Real-time Data**: Combines trained model predictions with live NASA feeds

## API Endpoints

### POST `/recommend`
Get personalized space event recommendations.

**Request Body:**
```json
{
    "event_type": "meteor shower",
    "location": "USA",
    "time_of_day": "night",
    "include_nasa": true
}
```

**Response:**
```json
{
    "user_preferences": {
        "event_type": "meteor shower",
        "location": "USA",
        "time_of_day": "night",
        "include_nasa": true
    },
    "recommendations": [
        {
            "event_type": "meteor shower",
            "location": "USA",
            "time_of_day": "night",
            "duration": 120,
            "popularity_score": 8.5,
            "predicted_like": 1,
            "like_probability": 0.85,
            "reason": "Based on your preferences",
            "source": "Trained Model"
        },
        {
            "event_type": "nasa_apod",
            "location": "Global",
            "time_of_day": "any",
            "duration": 60,
            "popularity_score": 9.0,
            "predicted_like": 1,
            "like_probability": 0.9,
            "reason": "Live NASA data",
            "source": "NASA APOD",
            "title": "Astronomy Picture of the Day",
            "description": "Daily space image from NASA",
            "date": "2024-01-15",
            "image_url": "https://apod.nasa.gov/apod/image/..."
        }
    ],
    "total_recommendations": 3,
    "nasa_events_included": 1,
    "timestamp": "2024-01-15T10:30:00"
}
```

### GET `/nasa/events`
Get live NASA space events.

**Response:**
```json
{
    "events": [
        {
            "event_type": "nasa_apod",
            "title": "Astronomy Picture of the Day",
            "description": "Daily space image from NASA",
            "date": "2024-01-15",
            "image_url": "https://apod.nasa.gov/apod/image/...",
            "source": "NASA APOD",
            "popularity_score": 9.0,
            "duration": 60,
            "time_of_day": "any",
            "location": "Global"
        },
        {
            "event_type": "near_earth_asteroid",
            "title": "Asteroid 2024 AB",
            "description": "Near-Earth asteroid passing by today",
            "date": "2024-01-15",
            "distance_km": "1234567.89",
            "velocity_kmh": "45000.00",
            "source": "NASA NEO",
            "popularity_score": 8.5,
            "duration": 120,
            "time_of_day": "night",
            "location": "Global"
        }
    ],
    "total_events": 2,
    "timestamp": "2024-01-15T10:30:00"
}
```

### GET `/health`
Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "model_loaded": true,
    "nasa_api_key": "configured"
}
```

### GET `/model/info`
Get information about the trained model.

**Response:**
```json
{
    "model_type": "DecisionTreeClassifier",
    "feature_names": ["event_type_meteor shower", "location_USA", ...],
    "training_data_size": 40,
    "available_event_types": ["meteor shower", "solar eclipse", ...],
    "available_locations": ["USA", "Europe", "Asia", ...]
}
```

### GET `/events`
Get all available events from the training dataset.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train the Model
```bash
python train_model.py
```

This will:
- Load the `events.csv` dataset
- Preprocess the data (one-hot encoding for categorical features, scaling for numerical features)
- Train a DecisionTreeClassifier
- Save the model as `space_events_model.pkl`
- Save the training data as `events_data.pkl`

### 3. Configure NASA API (Optional)
For enhanced functionality, get a free NASA API key from [https://api.nasa.gov/](https://api.nasa.gov/)

Set the environment variable:
```bash
export NASA_API_KEY=your_api_key_here
```

Or on Windows:
```cmd
set NASA_API_KEY=your_api_key_here
```

### 4. Start the API
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Dataset Structure

The `events.csv` file contains the following columns:

- `event_type`: Type of space event (meteor shower, solar eclipse, etc.)
- `location`: Geographic location (USA, Europe, Asia, etc.)
- `time_of_day`: Time of day (day, night)
- `duration`: Event duration in minutes
- `popularity_score`: Popularity rating (0-10)
- `liked`: Binary target variable (0 or 1)

## Testing the API

### Using the Test Script
```bash
python test_recommendation_api.py
```

### Using curl
```bash
# Test recommendation
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "meteor shower",
    "location": "USA",
    "time_of_day": "night",
    "include_nasa": true
  }'

# Test NASA events
curl http://localhost:5000/nasa/events

# Test health check
curl http://localhost:5000/health
```

### Using Python requests
```python
import requests

# Get recommendations
response = requests.post('http://localhost:5000/recommend', json={
    'event_type': 'meteor shower',
    'location': 'USA',
    'time_of_day': 'night',
    'include_nasa': True
})

recommendations = response.json()
print(f"Found {recommendations['total_recommendations']} recommendations")
```

## Model Details

### Training Process
1. **Data Preprocessing**:
   - One-hot encoding for categorical features (event_type, location, time_of_day)
   - Standard scaling for numerical features (duration, popularity_score)

2. **Model Training**:
   - DecisionTreeClassifier with max_depth=10
   - Random state for reproducibility
   - Pipeline with preprocessor and classifier

3. **Feature Importance**:
   - The model learns which features are most important for predicting user preferences
   - Popularity score and event type are typically the most important features

### Recommendation Logic
1. **User Preferences**: Takes user's preferred event type, location, and time of day
2. **Model Prediction**: Uses the trained model to predict which events the user would like
3. **NASA Integration**: Includes live NASA data (APOD and near-Earth asteroids)
4. **Ranking**: Combines model predictions with NASA data and ranks by like probability
5. **Selection**: Returns top 3 recommendations

## Error Handling

The API includes comprehensive error handling:

- **Missing Required Fields**: Returns 400 error with specific field names
- **Invalid Data**: Validates input data types and ranges
- **NASA API Failures**: Gracefully handles NASA API timeouts and errors
- **Model Loading**: Checks for required model files on startup

## Performance Considerations

- **NASA API Rate Limits**: The NASA API has rate limits (1000 requests per hour for DEMO_KEY)
- **Model Loading**: Model is loaded once at startup for better performance
- **Caching**: Consider implementing caching for NASA API responses
- **Async Processing**: For production, consider async processing for NASA API calls

## Troubleshooting

### Common Issues

1. **Model Not Found**
   ```
   Error: Model file not found. Please run train_model.py first.
   ```
   Solution: Run `python train_model.py` to create the model files.

2. **NASA API Errors**
   ```
   Error fetching NASA APOD: 403 Forbidden
   ```
   Solution: Check your NASA API key or use DEMO_KEY for testing.

3. **Port Already in Use**
   ```
   Error: [Errno 98] Address already in use
   ```
   Solution: Change the port in `app.py` or kill the existing process.

### Debug Mode
Run the API in debug mode for detailed error messages:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Future Enhancements

- **User Feedback**: Implement user feedback collection to improve recommendations
- **More NASA APIs**: Integrate additional NASA APIs (Mars Rover, Space Weather, etc.)
- **Real-time Events**: Add real-time space event tracking
- **Geolocation**: Use user's actual location for more relevant recommendations
- **Advanced ML**: Implement more sophisticated recommendation algorithms
- **Caching**: Add Redis caching for better performance
- **Authentication**: Add user authentication and personalized recommendations

## License

This project is open source and available under the MIT License. 