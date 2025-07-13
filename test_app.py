# python-web-app/tests/test_app.py
import pytest
from app import app, db, Task # Import Task model directly from app.py now
from config import Config

# Use an in-memory SQLite database for testing
class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory SQLite for tests
    DEBUG = True
    TESTING = True # Enable Flask testing mode

@pytest.fixture(scope='module') # Run once for the module
def client():
    app.config.from_object(TestConfig) # Use test configuration
    with app.app_context():
        db.create_all() # Create tables for tests
        yield app.test_client() # Provide the client
        db.session.remove()
        db.drop_all() # Drop tables after tests

@pytest.fixture(autouse=True) # Run before each test
def clear_database():
    with app.app_context():
        # Clear data between tests to ensure isolation
        # Use Task model directly now that it's in app.py
        db.session.query(Task).delete()
        db.session.commit()

def test_index_page(client):
    """Test that the index page loads."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"My Task Manager" in rv.data
    assert b"No tasks yet!" in rv.data

def test_add_task(client):
    """Test adding a new task."""
    response = client.post('/add', data={'description': 'Test Task 1'}, follow_redirects=True)
    assert response.status_code == 200 # Should be 200 after redirect
    assert b"Test Task 1" in response.data

def test_complete_task(client):
    """Test marking a task as complete."""
    # Add a task first
    client.post('/add', data={'description': 'Task to Complete'}, follow_redirects=True)
    
    # Get the ID of the task
    with app.app_context():
        task = Task.query.filter_by(description='Task to Complete').first()
        assert task is not None
        task_id = task.id

    response = client.get(f'/complete/{task_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'<li class="completed">' in response.data # Check for completed class in HTML

def test_delete_task(client):
    """Test deleting a task."""
    # Add a task first
    client.post('/add', data={'description': 'Task to Delete'}, follow_redirects=True)
    
    # Get the ID of the task
    with app.app_context():
        task = Task.query.filter_by(description='Task to Delete').first()
        assert task is not None
        task_id = task.id

    response = client.get(f'/delete/{task_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b"Task to Delete" not in response.data # Ensure it's gone from the page

def test_health_check(client):
    """Test the health check endpoint."""
    rv = client.get('/health')
    assert rv.status_code == 200
    assert b"healthy" in rv.data # Check for the 'healthy' text response
