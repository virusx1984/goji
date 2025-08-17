# goji/app/schemas/master_data_schemas.py
from ..extensions import ma
from ..models.master_data_models import (
    Material, SupplierLocation, SupplierRelationship, Customer, CustomerLocation,
    Supplier, Product, Operation, Asset, AssetGroup, WorkCenter
)
from ..models.organization_models import BusinessUnit, LegalEntity, FactoryCluster, Plant

# =============================================
# Master Data & Organization Schemas
# =============================================

class CustomerLocationSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the CustomerLocation model."""
    class Meta:
        model = CustomerLocation
        fields = ("id", "cust_id", "loc_name", "loc_code", "address", 
                  "contact_person", "phone", "is_default")
        load_instance = True

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Customer model, including nested locations."""
    locations = ma.Nested(CustomerLocationSchema, many=True, dump_only=True)

    class Meta:
        model = Customer
        fields = ("id", "code", "name", "locations")
        load_instance = True

class SupplierSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Supplier model."""
    class Meta:
        model = Supplier
        fields = ("id", "code", "name", "supplier_type")
        load_instance = True

class SupplierLocationSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the SupplierLocation model, with nested supplier info."""
    supplier = ma.Nested(SupplierSchema, dump_only=True)
    materials_supplied = ma.Nested('SupplierRelationshipSchema', many=True, dump_only=True)

    class Meta:
        model = SupplierLocation
        fields = ("id", "supplier_id", "loc_name", "loc_code", "address", 
                  "contact_person", "phone", "is_default", "supplier", "materials_supplied")
        load_instance = True

class SupplierRelationshipSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the SupplierRelationship model."""
    supplier_location = ma.String(attribute="supplier_location.loc_name", dump_only=True)
    supplier_code = ma.String(attribute="supplier_location.supplier.code", dump_only=True)

    class Meta:
        model = SupplierRelationship
        fields = ("id", "material_id", "sup_loc_id", "supplier_part_num", 
                  "is_preferred", "supplier_location", "supplier_code")
        load_instance = True

class MaterialSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Material model, with nested suppliers."""
    suppliers = ma.Nested(SupplierRelationshipSchema, many=True, dump_only=True)

    class Meta:
        model = Material
        fields = ("id", "part_num", "material_type", "name", "description", 
                  "uom", "length", "width", "thickness", "suppliers")
        load_instance = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Product model, with nested customer info."""
    customer = ma.Nested(CustomerSchema, exclude=("locations",), dump_only=True)

    class Meta:
        model = Product
        fields = ("id", "product_status", "ref_product_id", "cust_id", 
                  "cust_part_num", "cust_ver", "description", 
                  "pcs_per_strip", "strips_per_panel", "customer")
        load_instance = True

class OperationSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Operation model."""
    class Meta:
        model = Operation
        fields = ("id", "code", "name", "description")
        load_instance = True

class AssetGroupSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the AssetGroup model."""
    class Meta:
        model = AssetGroup
        fields = ("id", "plant_id", "name", "group_status", "description")
        load_instance = True

class AssetSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Asset model, with nested related info."""
    asset_group = ma.Nested(AssetGroupSchema, dump_only=True)
    supplier_location = ma.Nested(SupplierLocationSchema, exclude=("materials_supplied", "supplier"), dump_only=True)
    manufacturer = ma.Nested(SupplierSchema, dump_only=True)

    class Meta:
        model = Asset
        fields = ("id", "asset_group_id", "asset_tag", "serial_num", "model_num",
                  "sup_loc_id", "mfg_id", "purchase_date", "install_date", 
                  "asset_status", "asset_group", "supplier_location", "manufacturer")
        load_instance = True

class WorkCenterSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the WorkCenter model, including its associated assets."""
    assets = ma.Nested(AssetSchema, many=True, dump_only=True)

    class Meta:
        model = WorkCenter
        fields = ("id", "plant_id", "name", "description", 
                  "daily_avail_sec", "oee_pct", "assets")
        load_instance = True

class BusinessUnitSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the BusinessUnit model."""
    class Meta:
        model = BusinessUnit
        fields = ("id", "name", "description")
        load_instance = True

class LegalEntitySchema(ma.SQLAlchemyAutoSchema):
    """Schema for the LegalEntity model."""
    class Meta:
        model = LegalEntity
        fields = ("id", "name", "tax_id", "address", "legal_rep")
        load_instance = True

class FactoryClusterSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the FactoryCluster model, with nested BU and Legal Entity."""
    business_unit = ma.Nested(BusinessUnitSchema, dump_only=True)
    legal_entity = ma.Nested(LegalEntitySchema, dump_only=True)

    class Meta:
        model = FactoryCluster
        fields = ("id", "bu_id", "legal_entity_id", "name", 
                  "business_unit", "legal_entity")
        load_instance = True

class PlantSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Plant model, with nested cluster info."""
    factory_cluster = ma.Nested(FactoryClusterSchema, exclude=("business_unit", "legal_entity"), dump_only=True)

    class Meta:
        model = Plant
        fields = ("id", "cluster_id", "name", "address", "factory_cluster")
        load_instance = True
