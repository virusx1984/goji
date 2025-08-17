# goji/app/organization/schemas.py
from ..extensions import ma
from .models import BusinessUnit, LegalEntity, FactoryCluster, Plant

# =============================================
# Organization Schemas
# =============================================

class BusinessUnitSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the BusinessUnit model."""
    class Meta:
        model = BusinessUnit
        load_instance = True

class LegalEntitySchema(ma.SQLAlchemyAutoSchema):
    """Schema for the LegalEntity model."""
    class Meta:
        model = LegalEntity
        load_instance = True

class FactoryClusterSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the FactoryCluster model, with nested BU and Legal Entity."""
    # Nest related objects to provide more context in the API response
    business_unit = ma.Nested(BusinessUnitSchema, dump_only=True)
    legal_entity = ma.Nested(LegalEntitySchema, dump_only=True)

    class Meta:
        model = FactoryCluster
        load_instance = True

class PlantSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Plant model, with nested cluster info."""
    # Nest the parent cluster for context, but exclude its own nested objects
    # to keep the payload lean.
    factory_cluster = ma.Nested(FactoryClusterSchema, exclude=("business_unit", "legal_entity"), dump_only=True)

    class Meta:
        model = Plant
        load_instance = True
