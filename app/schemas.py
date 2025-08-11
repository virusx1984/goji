# goji/app/schemas.py 

from . import ma
from .models.master_data_models import (
    Material, SupplierLocation, SupplierRelationship, Customer, CustomerLocation,
    Supplier, Product, Operation, Asset, AssetGroup, WorkCenter
)
from .models.organization_models import BusinessUnit, LegalEntity, FactoryCluster, Plant
from .models.user_permission_models import User, Role, Permission, Menu

# =============================================
# Master Data Schemas
# =============================================

class CustomerLocationSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the CustomerLocation model.
    """
    class Meta:
        model = CustomerLocation
        fields = ("id", "cust_id", "loc_name", "loc_code", "address", 
                  "contact_person", "phone", "is_default", 
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the Customer model.
    Manages customer (Bill-To) information.
    """
    locations = ma.Nested(CustomerLocationSchema, many=True, dump_only=True)

    class Meta:
        model = Customer
        fields = ("id", "code", "name", "locations", 
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

class SupplierSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the Supplier model.
    Manages supplier information.
    """
    class Meta:
        model = Supplier
        fields = ("id", "code", "name", "supplier_type",
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

class SupplierLocationSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the SupplierLocation model.
    Includes basic supplier information nested.
    """
    supplier = ma.Nested(SupplierSchema, exclude=("created_at", "updated_at", "created_by_id", "updated_by_id"), dump_only=True) # Nested supplier info
    materials_supplied = ma.Nested('SupplierRelationshipSchema', many=True, dump_only=True) # Forward reference

    class Meta:
        model = SupplierLocation
        fields = ("id", "supplier_id", "loc_name", "loc_code", "address", 
                  "contact_person", "phone", "is_default", "supplier", "materials_supplied",
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

class SupplierRelationshipSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the SupplierRelationship model.
    This replaces the old to_dict() method and adds nested information.
    """
    supplier_location = ma.String(attribute="supplier_location.loc_name", dump_only=True)
    supplier_code = ma.String(attribute="supplier_location.supplier.code", dump_only=True)
    # If you need more detailed supplier_location or material info, you can nest their full schemas:
    # supplier_location_detail = ma.Nested(SupplierLocationSchema, exclude=("materials_supplied",), dump_only=True)
    # material_detail = ma.Nested('MaterialSchema', exclude=("suppliers",), dump_only=True)

    class Meta:
        model = SupplierRelationship
        fields = ("id", "material_id", "sup_loc_id", "supplier_part_num", 
                  "is_preferred", "supplier_location", "supplier_code",
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

class MaterialSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the Material model.
    """
    suppliers = ma.Nested(SupplierRelationshipSchema, many=True, dump_only=True)

    class Meta:
        model = Material
        fields = ("id", "part_num", "material_type", "name", "description", 
                  "uom", "length", "width", "thickness", "suppliers",
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the Product model.
    Core business data for customer products.
    """
    customer = ma.Nested(CustomerSchema, exclude=("locations", "products", "created_at", "updated_at", "created_by_id", "updated_by_id"), dump_only=True)
    # If you want to nest the reference product, handle recursion carefully
    # ref_product = ma.Nested('self', only=("id", "cust_part_num", "cust_ver"), dump_only=True)

    class Meta:
        model = Product
        fields = ("id", "product_status", "ref_product_id", "cust_id", 
                  "cust_part_num", "cust_ver", "description", 
                  "pcs_per_strip", "strips_per_panel", "customer",
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

class OperationSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the Operation model.
    Manages standard manufacturing operations.
    """
    class Meta:
        model = Operation
        fields = ("id", "code", "name", "description",
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

class AssetGroupSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the AssetGroup model.
    Manages asset groupings.
    """
    class Meta:
        model = AssetGroup
        fields = ("id", "plant_id", "name", "group_status", "description",
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

class AssetSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the Asset model.
    Manages physical assets.
    """
    asset_group = ma.Nested(AssetGroupSchema, exclude=("created_at", "updated_at", "created_by_id", "updated_by_id"), dump_only=True)
    supplier_location = ma.Nested(SupplierLocationSchema, exclude=("materials_supplied", "supplier", "created_at", "updated_at", "created_by_id", "updated_by_id"), dump_only=True)
    manufacturer = ma.Nested(SupplierSchema, exclude=("created_at", "updated_at", "created_by_id", "updated_by_id"), dump_only=True)

    class Meta:
        model = Asset
        fields = ("id", "asset_group_id", "asset_tag", "serial_num", "model_num",
                  "sup_loc_id", "mfg_id", "purchase_date", "install_date", 
                  "asset_status", "asset_group", "supplier_location", "manufacturer",
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

class WorkCenterSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the WorkCenter model.
    Core master data for capacity planning.
    """
    assets = ma.Nested(AssetSchema, many=True, dump_only=True, 
                        exclude=("created_at", "updated_at", "created_by_id", "updated_by_id")) # Now includes assets

    class Meta:
        model = WorkCenter
        fields = ("id", "plant_id", "name", "description", 
                  "daily_avail_sec", "oee_pct", "assets", # Add assets to fields
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

# =============================================
# Organization Schemas
# =============================================

class BusinessUnitSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the BusinessUnit model.
    """
    class Meta:
        model = BusinessUnit
        fields = ("id", "name", "description",
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

class LegalEntitySchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the LegalEntity model.
    """
    class Meta:
        model = LegalEntity
        fields = ("id", "name", "tax_id", "address", "legal_rep",
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

class FactoryClusterSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the FactoryCluster model.
    """
    business_unit = ma.Nested(BusinessUnitSchema, exclude=("created_at", "updated_at", "created_by_id", "updated_by_id"), dump_only=True)
    legal_entity = ma.Nested(LegalEntitySchema, exclude=("created_at", "updated_at", "created_by_id", "updated_by_id"), dump_only=True)

    class Meta:
        model = FactoryCluster
        fields = ("id", "bu_id", "legal_entity_id", "name", 
                  "business_unit", "legal_entity",
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

class PlantSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the Plant model.
    """
    factory_cluster = ma.Nested(FactoryClusterSchema, exclude=("business_unit", "legal_entity", "created_at", "updated_at", "created_by_id", "updated_by_id"), dump_only=True)

    class Meta:
        model = Plant
        fields = ("id", "cluster_id", "name", "address", "factory_cluster",
                  "created_at", "updated_at", "created_by_id", "updated_by_id")
        load_instance = True

# =============================================
# User & Permission Schemas
# =============================================

class PermissionSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the Permission model.
    Replaces to_dict().
    """
    class Meta:
        model = Permission
        fields = ("id", "name", "description", 
                  "created_at", "updated_at") # No created_by/updated_by for permissions themselves
        load_instance = True

class RoleSimpleSchema(ma.SQLAlchemyAutoSchema):
    """
    Simple Schema for the Role model, for nested display where full permissions aren't needed.
    Replaces to_dict_simple().
    """
    class Meta:
        model = Role
        fields = ("id", "name")
        load_instance = True

class RoleSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the Role model.
    Replaces to_dict().
    """
    permissions = ma.Nested(PermissionSchema, many=True, dump_only=True)

    class Meta:
        model = Role
        fields = ("id", "name", "description", "permissions", 
                  "created_at", "updated_at")
        load_instance = True

class UserSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the User model.
    Excludes password_hash. Replaces to_dict().
    """
    roles = ma.Nested(RoleSimpleSchema, many=True, dump_only=True) # Use RoleSimpleSchema for nesting

    class Meta:
        model = User
        fields = ("id", "username", "full_name", "email", "is_active", "roles",
                  "created_at", "updated_at")
        load_instance = True


class MenuSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for the Menu model.
    Handles recursive children. Replaces to_dict().
    """
    required_permission = ma.Nested(PermissionSchema, exclude=("created_at", "updated_at"), dump_only=True)
    # Use 'self' for recursive nesting
    children = ma.Nested('self', many=True, dump_only=True) 

    class Meta:
        model = Menu
        fields = ("id", "parent_id", "name", "route", "icon", "order_num", 
                  "required_permission_id", "required_permission", "children")
        load_instance = True

