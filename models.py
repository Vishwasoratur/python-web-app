# python-web-app/models.py
# This will be imported into app.py after db is initialized
# We define db in app.py and pass the app instance to SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from app import db # This line requires a specific order of import/init

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Task {self.id}: {self.description}>'
