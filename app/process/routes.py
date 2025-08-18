# goji/app/process/routes.py
from flask import Blueprint, jsonify
from .models import Routing
from .schemas import RoutingSchema

bp = Blueprint('process', __name__, url_prefix='/api/process')

routings_schema = RoutingSchema(many=True)

@bp.route('/routings', methods=['GET'])
def get_routings():
    """Get a list of all routings."""
    all_routings = Routing.query.all()
    return jsonify(routings_schema.dump(all_routings))

# NOTE: Add other CRUD endpoints for process models as needed.
