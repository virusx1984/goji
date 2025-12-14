# goji/app/process/services.py

from ..extensions import db
from .models import (
    Routing, RoutingOperation, OperationResource, 
    BomItem, AlternateMaterial, LayerDefinition, LayerStructure
)
from .schemas import (
    RoutingSchema, RoutingOperationSchema, 
    LayerDefinitionSchema, LayerStructureSchema
)
from marshmallow import ValidationError

class ProcessService:
    """
    Encapsulates business logic for Manufacturing Processes 
    (Routings, BOMs, Resources, Layer Structures).
    """

    def __init__(self):
        self.routing_schema = RoutingSchema()
        self.routing_op_schema = RoutingOperationSchema()
        self.layer_def_schema = LayerDefinitionSchema()
        self.layer_struct_schema = LayerStructureSchema()

    # =========================================================
    # Routing Logic (Header & Structure)
    # =========================================================

    def get_all_routings(self):
        """Retrieves all routings."""
        return Routing.query.all()

    def get_routing_by_id(self, routing_id):
        """Retrieves a single routing by ID."""
        return Routing.query.get_or_404(routing_id)

    def create_routing(self, data: dict) -> Routing:
        """
        Creates a new routing. 
        Note: The Schema handles nested creation of Operations, Resources, and BOMs 
        if configured with load_instance=True and nested loads.
        """
        try:
            # Load data using schema (validates and creates instance)
            new_routing = self.routing_schema.load(data)
            
            db.session.add(new_routing)
            db.session.commit()
            return new_routing
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    def update_routing(self, routing_id: int, data: dict) -> Routing:
        """Updates an existing routing."""
        routing = self.get_routing_by_id(routing_id)
        try:
            # Partial update allows updating specific fields
            updated_routing = self.routing_schema.load(data, instance=routing, partial=True)
            db.session.commit()
            return updated_routing
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e
            
    def delete_routing(self, routing_id: int):
        """Deletes a routing."""
        routing = self.get_routing_by_id(routing_id)
        try:
            db.session.delete(routing)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    # =========================================================
    # Layer Definition Logic
    # =========================================================

    def get_all_layer_definitions(self):
        return LayerDefinition.query.all()

    def create_layer_definition(self, data: dict) -> LayerDefinition:
        try:
            new_layer = self.layer_def_schema.load(data)
            db.session.add(new_layer)
            db.session.commit()
            return new_layer
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    # =========================================================
    # Layer Structure Logic
    # =========================================================

    def get_layer_structures_by_routing(self, routing_id):
        return LayerStructure.query.filter_by(routing_id=routing_id).all()

# Singleton instance
process_service = ProcessService()

