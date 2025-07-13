# python-web-app/app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import logging
import os

# --- Import Configuration ---
from config import Config

app = Flask(__name__)
app.config.from_object(Config) # Load configuration

# --- Initialize Database ---
db = SQLAlchemy(app)

# --- Import Models (after db is initialized) ---
# This is a common pattern to avoid circular imports
from models import Item 

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Database Initialization on startup ---
with app.app_context():
    # Ensure the 'instance' directory exists for SQLite
    instance_path = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # Create database tables if they don't exist
    db.create_all()
    logger.info("Database tables ensured.")


# --- Routes (API Endpoints) ---

@app.route('/')
def home():
    logger.info("Serving home route.")
    return jsonify({"message": "Welcome to the Production-Ready Python API!"}), 200

@app.route('/health')
def health_check():
    # Attempt a simple DB query to ensure connection is healthy
    try:
        db.session.execute(db.select(Item)).first() 
        logger.info("Health check passed: DB connection OK.")
        return jsonify({"status": app.config['APP_STATUS'], "database": "connected"}), 200
    except Exception as e:
        logger.error(f"Health check failed: DB connection error - {e}")
        return jsonify({"status": "unhealthy", "database": "disconnected", "error": str(e)}), 500

@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400

    new_item = Item(name=data['name'], description=data.get('description'))
    
    try:
        db.session.add(new_item)
        db.session.commit()
        logger.info(f"Item created: {new_item.name} (ID: {new_item.id})")
        return jsonify(new_item.to_dict()), 201
    except IntegrityError:
        db.session.rollback() # Rollback in case of unique constraint violation
        logger.warning(f"Attempt to create duplicate item name: {data['name']}")
        return jsonify({"error": f"Item with name '{data['name']}' already exists"}), 409
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating item: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    logger.info(f"Retrieved {len(items)} items.")
    return jsonify([item.to_dict() for item in items]), 200

@app.route('/items/<int:item_id>', methods=['GET'])
def get_single_item(item_id):
    item = db.session.get(Item, item_id) # Using db.session.get for primary key lookup
    if not item:
        logger.warning(f"Item not found: ID {item_id}")
        return jsonify({"error": "Item not found"}), 404
    logger.info(f"Retrieved item: {item.name} (ID: {item_id})")
    return jsonify(item.to_dict()), 200

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = db.session.get(Item, item_id)
    if not item:
        logger.warning(f"Attempt to update non-existent item: ID {item_id}")
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    new_name = data.get('name')
    if new_name and new_name != item.name: # Only check for uniqueness if name is changing
        # Check for duplicate name if provided and different
        existing_item_with_name = Item.query.filter_by(name=new_name).first()
        if existing_item_with_name and existing_item_with_name.id != item_id:
            logger.warning(f"Attempt to update item {item_id} to duplicate name: {new_name}")
            return jsonify({"error": f"Item with name '{new_name}' already exists"}), 409
        item.name = new_name

    if 'description' in data: # Allow description to be updated or set to null
        item.description = data['description']

    try:
        db.session.commit()
        logger.info(f"Item updated: {item.name} (ID: {item_id})")
        return jsonify(item.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating item {item_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = db.session.get(Item, item_id)
    if not item:
        logger.warning(f"Attempt to delete non-existent item: ID {item_id}")
        return jsonify({"error": "Item not found"}), 404
    
    db.session.delete(item)
    db.session.commit()
    logger.info(f"Item deleted: ID {item_id}")
    return '', 204 # No Content

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True)
