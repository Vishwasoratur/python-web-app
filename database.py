# database.py
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()

def init_db(app: Flask):
    """Initializes the database with the Flask application."""
    db.init_app(app)
    with app.app_context():
        # Create tables based on models.
        # In a real production app, you'd use Alembic or similar for migrations.
        db.create_all()
