# test_app.py
import pytest
from app import app, db
from models import Item
from config import Config # Import Config to use in test setup

# Use an in-memory SQLite database for testing
class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True
    TESTING = True # Enable Flask testing mode

@pytest.fixture(scope='module') # Run once for the module
def client():
    app.config.from_object(TestConfig) # Use test configuration
    with app.app_context():
        db.create_all() # Create tables
        yield app.test_client() # Provide the client
        db.drop_all() # Drop tables after tests

@pytest.fixture(autouse=True) # Run before each test
def clear_database():
    with app.app_context():
        # Clear data between tests to ensure isolation
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

def test_home_route(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Welcome to the Production-Ready Python API!" in rv.data

def test_health_check(client):
    rv = client.get('/health')
    assert rv.status_code == 200
    assert b"healthy" in rv.data

def test_create_item(client):
    response = client.post('/items', json={'name': 'Test Item', 'description': 'A new test item'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Test Item'
    assert data['description'] == 'A new test item'
    assert 'id' in data

    # Test duplicate creation
    response = client.post('/items', json={'name': 'Test Item', 'description': 'Another one'})
    assert response.status_code == 409 # Conflict

def test_get_items_empty(client):
    response = client.get('/items')
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_items_with_data(client):
    client.post('/items', json={'name': 'Item 1'})
    client.post('/items', json={'name': 'Item 2'})
    response = client.get('/items')
    assert response.status_code == 200
    items = response.get_json()
    assert len(items) == 2
    assert items[0]['name'] == 'Item 1'
    assert items[1]['name'] == 'Item 2'

def test_get_single_item(client):
    create_response = client.post('/items', json={'name': 'Unique Item'})
    item_id = create_response.get_json()['id']
    response = client.get(f'/items/{item_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Unique Item'

def test_get_non_existent_item(client):
    response = client.get('/items/999')
    assert response.status_code == 404
    assert b"Item not found" in response.data

def test_update_item(client):
    create_response = client.post('/items', json={'name': 'Update Me'})
    item_id = create_response.get_json()['id']
    update_response = client.put(f'/items/{item_id}', json={'name': 'Updated Item', 'description': 'New desc'})
    assert update_response.status_code == 200
    data = update_response.get_json()
    assert data['name'] == 'Updated Item'
    assert data['description'] == 'New desc'

    get_response = client.get(f'/items/{item_id}')
    assert get_response.get_json()['name'] == 'Updated Item'

def test_update_item_partial(client):
    create_response = client.post('/items', json={'name': 'Partial Update', 'description': 'Original desc'})
    item_id = create_response.get_json()['id']
    update_response = client.put(f'/items/{item_id}', json={'description': 'Only desc changed'})
    assert update_response.status_code == 200
    data = update_response.get_json()
    assert data['name'] == 'Partial Update' # Name should remain
    assert data['description'] == 'Only desc changed'

def test_update_non_existent_item(client):
    response = client.put('/items/999', json={'name': 'Non Existent'})
    assert response.status_code == 404

def test_update_item_to_duplicate_name(client):
    client.post('/items', json={'name': 'Existing Item'})
    create_response = client.post('/items', json={'name': 'Another Item'})
    item_id = create_response.get_json()['id']

    response = client.put(f'/items/{item_id}', json={'name': 'Existing Item'})
    assert response.status_code == 409

def test_delete_item(client):
    create_response = client.post('/items', json={'name': 'Delete Me Too'})
    item_id = create_response.get_json()['id']
    delete_response = client.delete(f'/items/{item_id}')
    assert delete_response.status_code == 204 # No Content

    get_response = client.get(f'/items/{item_id}')
    assert get_response.status_code == 404

def test_delete_non_existent_item(client):
    response = client.delete('/items/999')
    assert response.status_code == 404
