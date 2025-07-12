# app.py
from flask import Flask, jsonify, request
from database import db, init_db
from models import Item
from config import Config
import logging
import sys

# --- Logging Setup ---
# Configure logging to output to stdout for Docker/Kubernetes logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) # Sends logs to stdout
    ]
)
logger = logging.getLogger(__name__)

# This is a test change to trigger CICD
# --- Flask App Initialization ---
app = Flask(__name__)
app.config.from_object(Config) # Load configuration from Config object
init_db(app) # Initialize database

# --- Error Handlers ---
@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify(message="Resource not found"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback() # Rollback any pending database transactions
    logger.error(f"500 Internal Server Error: {error}", exc_info=True)
    return jsonify(message="An unexpected error occurred"), 500

# --- Routes ---

@app.route('/')
def home():
    logger.info("Accessed home route.")
    return jsonify(message="Welcome to the Production-Ready Python API!"), 200

@app.route('/health')
def health_check():
    # A more robust health check could try to connect to the database
    try:
        db.session.execute(db.select(1)).scalar_one() # Simple query to check DB connection
        logger.info("Health check passed.")
        return jsonify(status="healthy", database="connected"), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify(status="unhealthy", database="disconnected", error=str(e)), 500

# --- CRUD Operations for Items ---

@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    if not data or 'name' not in data:
        logger.warning("Attempted to create item without 'name'.")
        return jsonify(message="Name is required"), 400

    name = data['name']
    description = data.get('description')

    if Item.query.filter_by(name=name).first():
        logger.warning(f"Attempted to create duplicate item: {name}")
        return jsonify(message=f"Item with name '{name}' already exists"), 409 # Conflict

    new_item = Item(name=name, description=description)
    try:
        db.session.add(new_item)
        db.session.commit()
        logger.info(f"Created new item: {new_item.name}")
        return jsonify(new_item.to_dict()), 201 # Created
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating item {name}: {e}", exc_info=True)
        return jsonify(message="Failed to create item"), 500

@app.route('/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    logger.info(f"Retrieved {len(items)} items.")
    return jsonify([item.to_dict() for item in items]), 200

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        logger.warning(f"Item with ID {item_id} not found.")
        return jsonify(message="Item not found"), 404
    logger.info(f"Retrieved item: {item.name}")
    return jsonify(item.to_dict()), 200

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        logger.warning(f"Attempted to update non-existent item ID: {item_id}")
        return jsonify(message="Item not found"), 404

    data = request.get_json()
    if not data:
        return jsonify(message="No data provided for update"), 400

    try:
        if 'name' in data:
            # Check for duplicate name if updating name
            existing_item = Item.query.filter_by(name=data['name']).first()
            if existing_item and existing_item.id != item_id:
                logger.warning(f"Attempted to update item {item_id} to duplicate name: {data['name']}")
                return jsonify(message=f"Item with name '{data['name']}' already exists"), 409

            item.name = data['name']
        if 'description' in data:
            item.description = data['description']

        db.session.commit()
        logger.info(f"Updated item ID: {item_id}")
        return jsonify(item.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating item {item_id}: {e}", exc_info=True)
        return jsonify(message="Failed to update item"), 500

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        logger.warning(f"Attempted to delete non-existent item ID: {item_id}")
        return jsonify(message="Item not found"), 404

    try:
        db.session.delete(item)
        db.session.commit()
        logger.info(f"Deleted item ID: {item_id}")
        return jsonify(message="Item deleted successfully"), 204 # No Content
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting item {item_id}: {e}", exc_info=True)
        return jsonify(message="Failed to delete item"), 500

if __name__ == '__main__':
    # In development, you can run this directly. Gunicorn is for production.
    app.run(host='0.0.0.0', port=5000)