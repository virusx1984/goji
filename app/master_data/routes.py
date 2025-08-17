# goji/app/apis/customers.py
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

# Use relative imports to get modules from the parent directory
from ..extensions import db 
from ..models.master_data_models import Customer
from ..schemas import CustomerSchema

# --- Key Change: Create its own Blueprint for this file ---
bp = Blueprint('customers', __name__, url_prefix='/api')

# Instantiate schemas for reuse
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

@bp.route('/customers', methods=['GET'])
def get_customers():
    """Retrieves a list of all customers."""
    all_customers = Customer.query.all()
    # The schema handles the conversion of all objects to a list of dicts
    return jsonify(customers_schema.dump(all_customers))

@bp.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    """Retrieves a single customer by their ID."""
    customer = Customer.query.get_or_404(id)
    # The schema handles the conversion of a single object
    return jsonify(customer_schema.dump(customer))

@bp.route('/customers', methods=['POST'])
def create_customer():
    """Creates a new customer from posted JSON data."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        # Validate and deserialize input data to a Customer model instance
        new_customer = customer_schema.load(json_data)
        db.session.add(new_customer)
        db.session.commit()
        # Return the data of the newly created customer, serialized by the schema
        return jsonify(customer_schema.dump(new_customer)), 201
    except ValidationError as err:
        # Return validation errors
        return jsonify(err.messages), 400

@bp.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    """Updates an existing customer."""
    customer = Customer.query.get_or_404(id)
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        # Load data into the existing customer instance (instance=customer)
        # Allow partial updates (partial=True)
        updated_customer = customer_schema.load(json_data, instance=customer, partial=True)
        db.session.commit()
        return jsonify(customer_schema.dump(updated_customer)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400

@bp.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    """Deletes a customer."""
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return '', 204 # No Content
