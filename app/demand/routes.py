# goji/app/demand/routes.py

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

# --- Service Layer Import ---
from .services import demand_service
from .schemas import SalesOrderSchema, ForecastSetSchema

bp = Blueprint('demand', __name__, url_prefix='/api/demand')

# Instantiate schemas for serialization (Dump only)
sales_order_schema = SalesOrderSchema()
sales_orders_schema = SalesOrderSchema(many=True)
forecast_set_schema = ForecastSetSchema()
forecast_sets_schema = ForecastSetSchema(many=True)

# =============================================
# Sales Order API Endpoints
# =============================================

@bp.route('/sales-orders', methods=['GET'])
def get_sales_orders():
    """Get a list of all sales orders."""
    all_orders = demand_service.get_all_sales_orders()
    return jsonify(sales_orders_schema.dump(all_orders))

@bp.route('/sales-orders/<int:id>', methods=['GET'])
def get_sales_order(id):
    """Get a single sales order by ID."""
    order = demand_service.get_sales_order_by_id(id)
    return jsonify(sales_order_schema.dump(order))

@bp.route('/sales-orders', methods=['POST'])
def create_sales_order():
    """Create a new sales order (with nested lines)."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_order = demand_service.create_sales_order(json_data)
        return jsonify(sales_order_schema.dump(new_order)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/sales-orders/<int:id>', methods=['PUT'])
def update_sales_order(id):
    """Update an existing sales order."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        updated_order = demand_service.update_sales_order(id, json_data)
        return jsonify(sales_order_schema.dump(updated_order)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/sales-orders/<int:id>', methods=['DELETE'])
def delete_sales_order(id):
    """Delete a sales order."""
    try:
        demand_service.delete_sales_order(id)
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================
# Forecast API Endpoints
# =============================================

@bp.route('/forecasts', methods=['GET'])
def get_forecasts():
    """Get a list of all forecast sets."""
    all_forecasts = demand_service.get_all_forecast_sets()
    return jsonify(forecast_sets_schema.dump(all_forecasts))

@bp.route('/forecasts', methods=['POST'])
def create_forecast():
    """Create a new forecast set."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_forecast = demand_service.create_forecast_set(json_data)
        return jsonify(forecast_set_schema.dump(new_forecast)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500