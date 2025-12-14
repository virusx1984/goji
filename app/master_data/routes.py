# goji/app/master_data/routes.py

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

# --- Service Layer Import ---
from .services import md_service
from .schemas import (
    CustomerSchema, SupplierSchema, ProductSchema, 
    MaterialSchema, WorkCenterSchema
)

bp = Blueprint('master_data', __name__, url_prefix='/api')

# Instantiate schemas for serialization (Dump only)
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
supplier_schema = SupplierSchema()
suppliers_schema = SupplierSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
material_schema = MaterialSchema()
materials_schema = MaterialSchema(many=True)
wc_schema = WorkCenterSchema()
wcs_schema = WorkCenterSchema(many=True)

# =============================================
# Customer API Endpoints
# =============================================

@bp.route('/customers', methods=['GET'])
def get_customers():
    """Retrieves a list of all customers."""
    all_customers = md_service.get_all_customers()
    return jsonify(customers_schema.dump(all_customers))

@bp.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    """Retrieves a single customer by their ID."""
    customer = md_service.get_customer_by_id(id)
    return jsonify(customer_schema.dump(customer))

@bp.route('/customers', methods=['POST'])
def create_customer():
    """Creates a new customer."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_customer = md_service.create_customer(json_data)
        return jsonify(customer_schema.dump(new_customer)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    """Updates an existing customer."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        updated_customer = md_service.update_customer(id, json_data)
        return jsonify(customer_schema.dump(updated_customer)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    """Deletes a customer."""
    try:
        md_service.delete_customer(id)
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================
# Other Master Data Endpoints (Examples)
# =============================================

@bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    suppliers = md_service.get_all_suppliers()
    return jsonify(suppliers_schema.dump(suppliers))

@bp.route('/suppliers', methods=['POST'])
def create_supplier():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_supplier = md_service.create_supplier(json_data)
        return jsonify(supplier_schema.dump(new_supplier)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/materials', methods=['GET'])
def get_materials():
    materials = md_service.get_all_materials()
    return jsonify(materials_schema.dump(materials))

@bp.route('/products', methods=['GET'])
def get_products():
    products = md_service.get_all_products()
    return jsonify(products_schema.dump(products))