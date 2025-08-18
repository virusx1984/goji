# goji/app/process/schemas.py
from ..extensions import ma
from .models import (
    Routing, RoutingOperation, LayerDefinition, LayerStructure,
    OperationResource, BomItem, AlternateMaterial, MaterialSupplier
)

class AlternateMaterialSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AlternateMaterial
        load_instance = True

class BomItemSchema(ma.SQLAlchemyAutoSchema):
    alternates = ma.Nested(AlternateMaterialSchema, many=True, dump_only=True)
    class Meta:
        model = BomItem
        load_instance = True
        include_relationships = True

class OperationResourceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OperationResource
        load_instance = True
        include_relationships = True

class RoutingOperationSchema(ma.SQLAlchemyAutoSchema):
    resources = ma.Nested(OperationResourceSchema, many=True, dump_only=True)
    bom_items = ma.Nested(BomItemSchema, many=True, dump_only=True)
    class Meta:
        model = RoutingOperation
        load_instance = True
        include_relationships = True

class RoutingSchema(ma.SQLAlchemyAutoSchema):
    operations = ma.Nested(RoutingOperationSchema, many=True, dump_only=True)
    class Meta:
        model = Routing
        load_instance = True
        include_relationships = True

class LayerDefinitionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LayerDefinition
        load_instance = True

class LayerStructureSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LayerStructure
        load_instance = True
        include_relationships = True

class MaterialSupplierSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MaterialSupplier
        load_instance = True
        include_relationships = True
