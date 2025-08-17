# goji/app/master_data/schemas.py
from ..extensions import ma
from .models import (
    Customer, 
    CustomerLocation,
    Supplier,
    SupplierLocation,
    Product,
    Material,
    Operation,
    Asset,
    AssetGroup,
    WorkCenter,
    SupplierRelationship,
)

from ..organization import(
    BusinessUnit,
    LegalEntity,
    FactoryCluster,
    Plant,
)

# =============================================
# Master Data & Organization Schemas
# =============================================

class CustomerLocationSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the CustomerLocation model."""
    class Meta:
        model = CustomerLocation
        load_instance = True

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Customer model, including nested locations."""
    locations = ma.Nested(CustomerLocationSchema, many=True, dump_only=True)

    class Meta:
        model = Customer
        load_instance = True

class SupplierSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Supplier model."""
    class Meta:
        model = Supplier
        load_instance = True

class SupplierLocationSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the SupplierLocation model, with nested supplier info."""
    supplier = ma.Nested(SupplierSchema, dump_only=True)
    materials_supplied = ma.Nested('SupplierRelationshipSchema', many=True, dump_only=True)

    class Meta:
        model = SupplierLocation
        load_instance = True

class SupplierRelationshipSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the SupplierRelationship model."""
    supplier_location = ma.String(attribute="supplier_location.loc_name", dump_only=True)
    supplier_code = ma.String(attribute="supplier_location.supplier.code", dump_only=True)

    class Meta:
        model = SupplierRelationship
        load_instance = True

class MaterialSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Material model, with nested suppliers."""
    suppliers = ma.Nested(SupplierRelationshipSchema, many=True, dump_only=True)

    class Meta:
        model = Material
        load_instance = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Product model, with nested customer info."""
    customer = ma.Nested(CustomerSchema, exclude=("locations",), dump_only=True)

    class Meta:
        model = Product
        load_instance = True

class OperationSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Operation model."""
    class Meta:
        model = Operation
        load_instance = True

class AssetGroupSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the AssetGroup model."""
    class Meta:
        model = AssetGroup
        load_instance = True

class AssetSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Asset model, with nested related info."""
    asset_group = ma.Nested(AssetGroupSchema, dump_only=True)
    supplier_location = ma.Nested(SupplierLocationSchema, exclude=("materials_supplied", "supplier"), dump_only=True)
    manufacturer = ma.Nested(SupplierSchema, dump_only=True)

    class Meta:
        model = Asset
        load_instance = True

class WorkCenterSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the WorkCenter model, including its associated assets."""
    assets = ma.Nested(AssetSchema, many=True, dump_only=True)

    class Meta:
        model = WorkCenter
        load_instance = True

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
    business_unit = ma.Nested(BusinessUnitSchema, dump_only=True)
    legal_entity = ma.Nested(LegalEntitySchema, dump_only=True)

    class Meta:
        model = FactoryCluster
        load_instance = True

class PlantSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Plant model, with nested cluster info."""
    factory_cluster = ma.Nested(FactoryClusterSchema, exclude=("business_unit", "legal_entity"), dump_only=True)

    class Meta:
        model = Plant
        load_instance = True
