# goji/app/process/routes.py

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

# --- Service Layer Import ---
from .services import process_service
from .schemas import (
    RoutingSchema, 
    LayerDefinitionSchema, 
    LayerStructureSchema
)

bp = Blueprint('process', __name__, url_prefix='/api/process')

# Instantiate schemas for serialization (Dump only)
routing_schema = RoutingSchema()
routings_schema = RoutingSchema(many=True)
layer_def_schema = LayerDefinitionSchema()
layer_defs_schema = LayerDefinitionSchema(many=True)
layer_struct_schema = LayerStructureSchema()
layer_structs_schema = LayerStructureSchema(many=True)

# =============================================
# Routing API Endpoints
# =============================================

@bp.route('/routings', methods=['GET'])
def get_routings():
    """Get a list of all routings."""
    all_routings = process_service.get_all_routings()
    return jsonify(routings_schema.dump(all_routings))

@bp.route('/routings/<int:id>', methods=['GET'])
def get_routing(id):
    """Get a single routing by ID."""
    routing = process_service.get_routing_by_id(id)
    return jsonify(routing_schema.dump(routing))

@bp.route('/routings', methods=['POST'])
def create_routing():
    """Create a new routing (can include nested operations/BOMs)."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_routing = process_service.create_routing(json_data)
        return jsonify(routing_schema.dump(new_routing)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/routings/<int:id>', methods=['PUT'])
def update_routing(id):
    """Update an existing routing."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        updated_routing = process_service.update_routing(id, json_data)
        return jsonify(routing_schema.dump(updated_routing)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/routings/<int:id>', methods=['DELETE'])
def delete_routing(id):
    """Delete a routing."""
    try:
        process_service.delete_routing(id)
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================
# Layer Definition API Endpoints
# =============================================

@bp.route('/layer-definitions', methods=['GET'])
def get_layer_definitions():
    """Get all layer definitions."""
    layers = process_service.get_all_layer_definitions()
    return jsonify(layer_defs_schema.dump(layers))

@bp.route('/layer-definitions', methods=['POST'])
def create_layer_definition():
    """Create a new layer definition."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_layer = process_service.create_layer_definition(json_data)
        return jsonify(layer_def_schema.dump(new_layer)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500