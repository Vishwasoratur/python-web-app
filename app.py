# python-web-app/app.py
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import os

app = Flask(__name__)

# --- Database Configuration ---
# Use a relative path for SQLite inside the container.
# This will create 'instance/tasks.db' inside the /app directory.
# This path is where Flask-SQLAlchemy will look for the database file.
# Note: For production with multiple replicas, you would use a shared volume or external DB.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Define the Task Model ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}: {self.description}>'

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Routes ---
@app.route('/')
def index():
    logger.info("Serving index page.")
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    description = request.form.get('description')
    if description:
        new_task = Task(description=description)
        db.session.add(new_task)
        db.session.commit()
        logger.info(f"Task added: {description} (ID: {new_task.id})")
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    logger.info(f"Task completed: {task.description} (ID: {task_id})")
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    logger.info(f"Task deleted with ID: {task_id}")
    return redirect(url_for('index'))

@app.route('/health')
def health_check():
    # Simple health check endpoint for Kubernetes
    # Also attempt to connect to DB to ensure it's healthy
    try:
        db.session.execute(db.select(Task)).first() # Or a simpler query
        logger.info("Health check passed: DB connection OK.")
        return 'OK', 200
    except Exception as e:
        logger.error(f"Health check failed: DB connection error - {e}")
        return 'DB Connection Failed', 500


# --- Database Initialization on startup ---
@app.before_first_request
def create_tables():
    # Ensure the 'instance' directory exists
    instance_path = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # Create database tables if they don't exist
    db.create_all()
    logger.info("Database tables ensured.")

# --- Application Entry Point ---
if __name__ == '__main__':
    logger.info("Starting Flask application...")
    # Manually create tables for local development outside Docker
    with app.app_context():
        create_tables() 
    app.run(host='0.0.0.0', port=5000, debug=True)
