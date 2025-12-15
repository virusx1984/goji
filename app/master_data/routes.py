# goji/app/master_data/routes.py

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

# --- Service Layer Import ---
from .services import md_service
from .schemas import (
    CustomerSchema, SupplierSchema, ProductSchema, InternalProductSchema,
    MaterialSchema, WorkCenterSchema, OperationSchema,
    AssetSchema, AssetGroupSchema
)

bp = Blueprint('master_data', __name__, url_prefix='/api')

# Instantiate schemas for serialization (Dump only)
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
supplier_schema = SupplierSchema()
suppliers_schema = SupplierSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
internal_product_schema = InternalProductSchema()
internal_products_schema = InternalProductSchema(many=True)
material_schema = MaterialSchema()
materials_schema = MaterialSchema(many=True)
wc_schema = WorkCenterSchema()
wcs_schema = WorkCenterSchema(many=True)
operation_schema = OperationSchema()
operations_schema = OperationSchema(many=True)
asset_schema = AssetSchema()
assets_schema = AssetSchema(many=True)
asset_group_schema = AssetGroupSchema()
asset_groups_schema = AssetGroupSchema(many=True)

# =============================================
# Customer API Endpoints
# =============================================
@bp.route('/customers', methods=['GET'])
def get_customers():
    all_customers = md_service.get_all_customers()
    return jsonify(customers_schema.dump(all_customers))

@bp.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = md_service.get_customer_by_id(id)
    return jsonify(customer_schema.dump(customer))

@bp.route('/customers', methods=['POST'])
def create_customer():
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
    try:
        md_service.delete_customer(id)
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================
# Product & Material Endpoints
# =============================================

@bp.route('/products', methods=['GET'])
def get_products():
    products = md_service.get_all_products()
    return jsonify(products_schema.dump(products))

@bp.route('/products', methods=['POST'])
def create_product():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_prod = md_service.create_product(json_data)
        return jsonify(product_schema.dump(new_prod)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/internal-products', methods=['GET'])
def get_internal_products():
    ips = md_service.get_all_internal_products()
    return jsonify(internal_products_schema.dump(ips))

@bp.route('/internal-products', methods=['POST'])
def create_internal_product():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_ip = md_service.create_internal_product(json_data)
        return jsonify(internal_product_schema.dump(new_ip)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/materials', methods=['GET'])
def get_materials():
    materials = md_service.get_all_materials()
    return jsonify(materials_schema.dump(materials))

@bp.route('/materials', methods=['POST'])
def create_material():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_mat = md_service.create_material(json_data)
        return jsonify(material_schema.dump(new_mat)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================
# Supplier Endpoints
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

# =============================================
# Resource Endpoints (WorkCenter, Operation, Asset)
# =============================================

@bp.route('/work-centers', methods=['GET'])
def get_work_centers():
    wcs = md_service.get_all_work_centers()
    return jsonify(wcs_schema.dump(wcs))

@bp.route('/work-centers/<int:id>', methods=['GET'])
def get_work_center(id):
    wc = md_service.get_work_center_by_id(id)
    return jsonify(wc_schema.dump(wc))

@bp.route('/work-centers', methods=['POST'])
def create_work_center():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_wc = md_service.create_work_center(json_data)
        return jsonify(wc_schema.dump(new_wc)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/operations', methods=['GET'])
def get_operations():
    ops = md_service.get_all_operations()
    return jsonify(operations_schema.dump(ops))

@bp.route('/operations', methods=['POST'])
def create_operation():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_op = md_service.create_operation(json_data)
        return jsonify(operation_schema.dump(new_op)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/assets', methods=['GET'])
def get_assets():
    assets = md_service.get_all_assets()
    return jsonify(assets_schema.dump(assets))

@bp.route('/assets', methods=['POST'])
def create_asset():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_asset = md_service.create_asset(json_data)
        return jsonify(asset_schema.dump(new_asset)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/asset-groups', methods=['GET'])
def get_asset_groups():
    groups = md_service.get_all_asset_groups()
    return jsonify(asset_groups_schema.dump(groups))

@bp.route('/asset-groups', methods=['POST'])
def create_asset_group():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_group = md_service.create_asset_group(json_data)
        return jsonify(asset_group_schema.dump(new_group)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500