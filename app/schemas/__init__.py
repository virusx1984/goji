# goji/app/schemas/__init__.py

# This file makes the 'schemas' directory a Python package.
# It also serves as a single point of entry to import all schemas,
# making it easier to access them from other parts of the application.

from .master_data_schemas import (
    CustomerSchema, 
    CustomerLocationSchema, 
    SupplierSchema, 
    SupplierLocationSchema, 
    SupplierRelationshipSchema, 
    MaterialSchema,
    ProductSchema, 
    OperationSchema, 
    AssetGroupSchema, 
    AssetSchema, 
    WorkCenterSchema, 
    BusinessUnitSchema, 
    LegalEntitySchema, 
    FactoryClusterSchema, 
    PlantSchema
)

from .user_management_schemas import (
    PermissionSchema, 
    RoleSchema, 
    RoleSimpleSchema,
    UserSchema, 
    MenuSchema
)
