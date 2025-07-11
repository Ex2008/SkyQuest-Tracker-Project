# Space Events Recommendation API

A Flask API that recommends space events based on user preferences using machine learning.

## Features

- **Machine Learning Model**: Uses DecisionTreeClassifier to predict user preferences
- **Data Preprocessing**: OneHotEncoder for categorical features, StandardScaler for numerical features
- **Recommendation Engine**: Returns top 3 recommended space events based on user input
- **RESTful API**: Clean JSON endpoints for easy integration

## Project Structure

```
├── events.csv              # Sample space events dataset
├── train_model.py          # Script to train and save the ML model
├── app.py                  # Flask API application
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Train the model**:
   ```bash
   python train_model.py
   ```
   This will create:
   - `space_events_model.pkl` (trained model)
   - `events_data.pkl` (processed dataset)

4. **Start the Flask server**:
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:5000`

## API Endpoints

### 1. POST `/recommend`
Get personalized space event recommendations.

**Request Body**:
```json
{
    "event_type": "meteor shower",
    "location": "USA",
    "time_of_day": "night"
}
```

**Response**:
```json
{
    "user_preferences": {
        "event_type": "meteor shower",
        "location": "USA",
        "time_of_day": "night"
    },
    "recommendations": [
        {
            "event_type": "meteor shower",
            "location": "USA",
            "time_of_day": "night",
            "duration": 120,
            "popularity_score": 8.5,
            "predicted_like": 1,
            "like_probability": 0.95,
            "reason": "Based on your preferences"
        }
    ],
    "total_recommendations": 3
}
```

### 2. GET `/health`
Health check endpoint.

**Response**:
```json
{
    "status": "healthy",
    "model_loaded": true
}
```

### 3. GET `/events`
Get all available events in the dataset.

**Response**:
```json
{
    "total_events": 50,
    "events": [
        {
            "event_type": "meteor shower",
            "location": "USA",
            "time_of_day": "night",
            "duration": 120,
            "popularity_score": 8.5,
            "liked": 1
        }
    ]
}
```

## Dataset Schema

The `events.csv` file contains the following columns:

- **event_type**: Type of space event (meteor shower, solar eclipse, etc.)
- **location**: Geographic location (USA, Europe, Asia, etc.)
- **time_of_day**: When the event occurs (day, night)
- **duration**: Event duration in minutes
- **popularity_score**: Popularity rating (0-10 scale)
- **liked**: Binary target variable (1 = liked, 0 = not liked)

## Available Event Types

- meteor shower
- solar eclipse
- lunar eclipse
- rocket launch
- comet viewing
- aurora borealis
- planetary conjunction
- star party

## Available Locations

- USA
- Canada
- Europe
- Asia
- Australia
- Africa
- South America
- Russia
- India
- Norway
- Sweden
- Finland
- Iceland

## Usage Examples

### Using curl:
```bash
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "meteor shower",
    "location": "USA",
    "time_of_day": "night"
  }'
```

### Using Python requests:
```python
import requests

url = "http://localhost:5000/recommend"
data = {
    "event_type": "meteor shower",
    "location": "USA",
    "time_of_day": "night"
}

response = requests.post(url, json=data)
recommendations = response.json()
print(recommendations)
```

## How It Works

1. **Data Preprocessing**: 
   - Categorical features (event_type, location, time_of_day) are encoded using OneHotEncoder
   - Numerical features (duration, popularity_score) are normalized using StandardScaler

2. **Model Training**:
   - DecisionTreeClassifier is trained to predict whether a user would "like" an event
   - The model learns patterns from the historical data in events.csv

3. **Recommendation Process**:
   - User preferences are processed through the same preprocessing pipeline
   - The model predicts the probability of the user liking different event combinations
   - Top 3 events with highest "like" probabilities are returned

4. **Fallback Strategy**:
   - If no events match the user's preferences, the API returns the most popular events

## Model Performance

The model typically achieves:
- Training accuracy: ~95-100% (on the sample dataset)
- Feature importance shows which factors most influence user preferences

## Customization

### Adding New Events
1. Add new rows to `events.csv`
2. Retrain the model: `python train_model.py`
3. Restart the Flask server

### Modifying the Model
Edit `train_model.py` to:
- Change the algorithm (RandomForest, XGBoost, etc.)
- Adjust hyperparameters
- Add new features

### Extending the API
Add new endpoints in `app.py` for:
- User feedback collection
- Model retraining
- Additional recommendation filters

## Troubleshooting

### Common Issues:

1. **"Model file not found" error**:
   - Run `python train_model.py` first

2. **Import errors**:
   - Install dependencies: `pip install -r requirements.txt`

3. **Port already in use**:
   - Change the port in `app.py` or kill the existing process

### Debug Mode:
The Flask app runs in debug mode by default. Check the console for detailed error messages.

## License

This project is for educational purposes. Feel free to modify and extend it for your needs.
