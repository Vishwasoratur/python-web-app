# python-web-app/config.py
import os

class Config:
    # Use a relative path for SQLite inside the container.
    # This will create 'instance/app.db' inside the /app directory.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for Flask sessions (not strictly needed for this API, but good practice)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-that-should-be-changed-in-prod'

    # Enable Flask debug mode for development (turn off in production)
    DEBUG = False
    TESTING = False # Default for production/dev

    # For the /health endpoint
    APP_STATUS = "healthy"
