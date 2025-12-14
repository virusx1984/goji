# goji/app/organization/routes.py

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from .services import org_service
from .schemas import (
    BusinessUnitSchema, 
    LegalEntitySchema, 
    FactoryClusterSchema, 
    PlantSchema
)

bp = Blueprint('organization', __name__, url_prefix='/api/organization')

# Instantiate schemas for serialization (Dump only)
bu_schema = BusinessUnitSchema()
bus_schema = BusinessUnitSchema(many=True)
le_schema = LegalEntitySchema()
les_schema = LegalEntitySchema(many=True)
fc_schema = FactoryClusterSchema()
fcs_schema = FactoryClusterSchema(many=True)
plant_schema = PlantSchema()
plants_schema = PlantSchema(many=True)


# =============================================
# Business Unit API Endpoints
# =============================================

@bp.route('/business-units', methods=['GET'])
def get_business_units():
    """Get a list of all business units."""
    all_bus = org_service.get_all_business_units()
    return jsonify(bus_schema.dump(all_bus))

@bp.route('/business-units', methods=['POST'])
def create_business_unit():
    """Create a new business unit."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_bu = org_service.create_business_unit(json_data)
        return jsonify(bu_schema.dump(new_bu)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================
# Legal Entity API Endpoints
# =============================================

@bp.route('/legal-entities', methods=['GET'])
def get_legal_entities():
    """Get a list of all legal entities."""
    all_les = org_service.get_all_legal_entities()
    return jsonify(les_schema.dump(all_les))

@bp.route('/legal-entities', methods=['POST'])
def create_legal_entity():
    """Create a new legal entity."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_le = org_service.create_legal_entity(json_data)
        return jsonify(le_schema.dump(new_le)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================
# Factory Cluster API Endpoints
# =============================================

@bp.route('/factory-clusters', methods=['GET'])
def get_factory_clusters():
    """Get a list of all factory clusters."""
    all_fcs = org_service.get_all_clusters()
    return jsonify(fcs_schema.dump(all_fcs))

@bp.route('/factory-clusters', methods=['POST'])
def create_factory_cluster():
    """Create a new factory cluster."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_fc = org_service.create_cluster(json_data)
        return jsonify(fc_schema.dump(new_fc)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================
# Plant API Endpoints
# =============================================

@bp.route('/plants', methods=['GET'])
def get_plants():
    """Get a list of all plants."""
    all_plants = org_service.get_all_plants()
    return jsonify(plants_schema.dump(all_plants))

@bp.route('/plants', methods=['POST'])
def create_plant():
    """Create a new plant."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        new_plant = org_service.create_plant(json_data)
        return jsonify(plant_schema.dump(new_plant)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500