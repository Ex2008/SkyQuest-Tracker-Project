import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os

def train_model():
    """
    Load the events dataset, preprocess it, train a DecisionTreeClassifier,
    and save the model and preprocessors.
    """
    
    # Load the dataset
    print("Loading dataset...")
    df = pd.read_csv('events.csv')
    
    # Separate features and target
    X = df.drop('liked', axis=1)
    y = df['liked']
    
    # Define categorical and numerical columns
    categorical_features = ['event_type', 'location', 'time_of_day']
    numerical_features = ['duration', 'popularity_score']
    
    # Create preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_features),
            ('num', StandardScaler(), numerical_features)
        ],
        remainder='drop'
    )
    
    # Create the full pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', DecisionTreeClassifier(random_state=42, max_depth=10))
    ])
    
    # Train the model
    print("Training model...")
    pipeline.fit(X, y)
    
    # Save the pipeline
    print("Saving model...")
    joblib.dump(pipeline, 'space_events_model.pkl')
    
    # Also save the original dataset for recommendations
    joblib.dump(df, 'events_data.pkl')
    
    # Print model accuracy
    train_score = pipeline.score(X, y)
    print(f"Training accuracy: {train_score:.3f}")
    
    # Print feature importance (if available)
    try:
        feature_names = (preprocessor.named_transformers_['cat']
                        .get_feature_names_out(categorical_features).tolist() + 
                        numerical_features)
        
        importances = pipeline.named_steps['classifier'].feature_importances_
        feature_importance = dict(zip(feature_names, importances))
        
        print("\nTop 10 most important features:")
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_features[:10]:
            print(f"{feature}: {importance:.3f}")
    except:
        print("Could not extract feature importance")
    
    print("\nModel training completed successfully!")
    print("Files saved:")
    print("- space_events_model.pkl (trained model)")
    print("- events_data.pkl (original dataset)")

if __name__ == "__main__":
    train_model() 