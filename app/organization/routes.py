# goji/app/organization/routes.py
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from ..extensions import db
from .models import BusinessUnit, LegalEntity, FactoryCluster, Plant
from .schemas import BusinessUnitSchema, LegalEntitySchema, FactoryClusterSchema, PlantSchema

# Create a Blueprint for this module
bp = Blueprint('organization', __name__, url_prefix='/api/organization')

# Instantiate schemas for reuse
bu_schema = BusinessUnitSchema()
bus_schema = BusinessUnitSchema(many=True)
le_schema = LegalEntitySchema()
les_schema = LegalEntitySchema(many=True)
fc_schema = FactoryClusterSchema()
fcs_schema = FactoryClusterSchema(many=True)
plant_schema = PlantSchema()
plants_schema = PlantSchema(many=True)

# NOTE: You should add @jwt_required() and permission checks to these routes later.

# =============================================
# Business Unit API Endpoints
# =============================================

@bp.route('/business-units', methods=['GET'])
def get_business_units():
    """Get a list of all business units."""
    all_bus = BusinessUnit.query.all()
    return jsonify(bus_schema.dump(all_bus))

@bp.route('/business-units', methods=['POST'])
def create_business_unit():
    """Create a new business unit."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_bu = bu_schema.load(json_data)
        db.session.add(new_bu)
        db.session.commit()
        return jsonify(bu_schema.dump(new_bu)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

# ... (You can add GET by ID, PUT, and DELETE for BusinessUnit following the same pattern)

# =============================================
# Legal Entity API Endpoints
# =============================================

@bp.route('/legal-entities', methods=['GET'])
def get_legal_entities():
    """Get a list of all legal entities."""
    all_les = LegalEntity.query.all()
    return jsonify(les_schema.dump(all_les))

@bp.route('/legal-entities', methods=['POST'])
def create_legal_entity():
    """Create a new legal entity."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_le = le_schema.load(json_data)
        db.session.add(new_le)
        db.session.commit()
        return jsonify(le_schema.dump(new_le)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

# ... (You can add GET by ID, PUT, and DELETE for LegalEntity)

# =============================================
# Factory Cluster API Endpoints
# =============================================

@bp.route('/factory-clusters', methods=['GET'])
def get_factory_clusters():
    """Get a list of all factory clusters."""
    all_fcs = FactoryCluster.query.all()
    return jsonify(fcs_schema.dump(all_fcs))

@bp.route('/factory-clusters', methods=['POST'])
def create_factory_cluster():
    """Create a new factory cluster."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_fc = fc_schema.load(json_data)
        db.session.add(new_fc)
        db.session.commit()
        return jsonify(fc_schema.dump(new_fc)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

# ... (You can add GET by ID, PUT, and DELETE for FactoryCluster)

# =============================================
# Plant API Endpoints
# =============================================

@bp.route('/plants', methods=['GET'])
def get_plants():
    """Get a list of all plants."""
    all_plants = Plant.query.all()
    return jsonify(plants_schema.dump(all_plants))

@bp.route('/plants', methods=['POST'])
def create_plant():
    """Create a new plant."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_plant = plant_schema.load(json_data)
        db.session.add(new_plant)
        db.session.commit()
        return jsonify(plant_schema.dump(new_plant)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

# ... (You can add GET by ID, PUT, and DELETE for Plant)
