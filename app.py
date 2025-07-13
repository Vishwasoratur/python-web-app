# python-web-app/app.py
from flask import Flask, render_template, request, redirect, url_for
import logging

app = Flask(__name__)

# Configure logging to see messages in kubectl logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for tasks
# In a real app, this would be a database
tasks = []
task_id_counter = 0

@app.route('/')
def index():
    logger.info("Serving index page.")
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    global task_id_counter
    description = request.form.get('description')
    if description:
        task_id_counter += 1
        tasks.append({
            'id': task_id_counter,
            'description': description,
            'completed': False
        })
        logger.info(f"Task added: {description} (ID: {task_id_counter})")
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = True
            logger.info(f"Task completed: {task['description']} (ID: {task_id})")
            break
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    global tasks
    original_len = len(tasks)
    tasks = [task for task in tasks if task['id'] != task_id]
    if len(tasks) < original_len:
        logger.info(f"Task deleted with ID: {task_id}")
    return redirect(url_for('index'))

@app.route('/health')
def health_check():
    # Simple health check endpoint for Kubernetes
    logger.info("Health check passed.")
    return 'OK', 200

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True) # debug=True is for local dev, not production images
