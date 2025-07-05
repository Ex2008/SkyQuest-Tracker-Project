import os
from datetime import datetime

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Model settings
    MODEL_PATH = 'space_events_model.pkl'
    DATA_PATH = 'events_data.pkl'
    
    # API settings
    MAX_RECOMMENDATIONS = 3
    DEFAULT_POPULARITY_THRESHOLD = 7.0
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # CORS settings
    CORS_ORIGINS = ['*']  # Allow all origins in development
    
    # Rate limiting (requests per minute)
    RATE_LIMIT = 100
    
    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Database settings (for future use)
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///space_events.db'
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # Development-specific settings
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # More lenient rate limiting for development
    RATE_LIMIT = 1000

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use test model and data files
    MODEL_PATH = 'test_space_events_model.pkl'
    DATA_PATH = 'test_events_data.pkl'
    
    # Disable rate limiting for tests
    RATE_LIMIT = 10000

class ProductionConfig(Config):
    """Production configuration"""
    
    # Production-specific settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required for production")
    
    # Stricter rate limiting for production
    RATE_LIMIT = 60
    
    # Production CORS origins
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # Use Redis for caching in production
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            # Set up file logging
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/space_events_api.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('Space Events API startup')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Environment-specific settings
def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])

# Feature flags
FEATURE_FLAGS = {
    'ENABLE_USER_FEEDBACK': True,
    'ENABLE_MODEL_RETRAINING': False,
    'ENABLE_ANALYTICS': True,
    'ENABLE_CACHING': True,
    'ENABLE_RATE_LIMITING': True,
}

# API versioning
API_VERSION = 'v1'
API_PREFIX = f'/api/{API_VERSION}'

# Event types and locations (for validation)
VALID_EVENT_TYPES = [
    'meteor shower',
    'solar eclipse', 
    'lunar eclipse',
    'rocket launch',
    'comet viewing',
    'aurora borealis',
    'planetary conjunction',
    'star party'
]

VALID_LOCATIONS = [
    'USA',
    'Canada', 
    'Europe',
    'Asia',
    'Australia',
    'Africa',
    'South America',
    'Russia',
    'India',
    'Norway',
    'Sweden',
    'Finland',
    'Iceland'
]

VALID_TIMES_OF_DAY = ['day', 'night']

# Validation functions
def validate_event_type(event_type):
    """Validate event type"""
    return event_type.lower() in [t.lower() for t in VALID_EVENT_TYPES]

def validate_location(location):
    """Validate location"""
    return location in VALID_LOCATIONS

def validate_time_of_day(time_of_day):
    """Validate time of day"""
    return time_of_day.lower() in [t.lower() for t in VALID_TIMES_OF_DAY]

def validate_user_preferences(preferences):
    """Validate user preferences"""
    errors = []
    
    if not validate_event_type(preferences.get('event_type', '')):
        errors.append(f"Invalid event_type. Must be one of: {VALID_EVENT_TYPES}")
    
    if not validate_location(preferences.get('location', '')):
        errors.append(f"Invalid location. Must be one of: {VALID_LOCATIONS}")
    
    if not validate_time_of_day(preferences.get('time_of_day', '')):
        errors.append(f"Invalid time_of_day. Must be one of: {VALID_TIMES_OF_DAY}")
    
    return errors 