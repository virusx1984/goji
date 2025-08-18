# goji/app/demand/routes.py
from flask import Blueprint, jsonify
from .models import SalesOrder
from .schemas import SalesOrderSchema

bp = Blueprint('demand', __name__, url_prefix='/api/demand')

sales_orders_schema = SalesOrderSchema(many=True)

@bp.route('/sales-orders', methods=['GET'])
def get_sales_orders():
    """Get a list of all sales orders."""
    all_orders = SalesOrder.query.all()
    return jsonify(sales_orders_schema.dump(all_orders))

# NOTE: Add other CRUD endpoints for demand models as needed.
