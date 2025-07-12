# config.py
import os

class Config:
    # Default database URI (for development, SQLite)
    # In production, this should point to a robust database like PostgreSQL/MySQL
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Suppress warning
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    SECRET_KEY = os.getenv('SECRET_KEY', 'a_very_secret_key_for_dev') # For Flask sessions/security
