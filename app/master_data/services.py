# goji/app/master_data/services.py

from ..extensions import db
from .models import (
    Customer, CustomerLocation, Supplier, SupplierLocation,
    Product, InternalProduct, Material, WorkCenter, Operation,
    Asset, AssetGroup
)
from .schemas import (
    CustomerSchema, SupplierSchema, ProductSchema, InternalProductSchema,
    MaterialSchema, WorkCenterSchema, OperationSchema,
    AssetSchema, AssetGroupSchema
)
from marshmallow import ValidationError

class MasterDataService:
    """
    Encapsulates business logic for Master Data entities.
    """

    def __init__(self):
        self.customer_schema = CustomerSchema()
        self.supplier_schema = SupplierSchema()
        self.product_schema = ProductSchema()
        self.internal_product_schema = InternalProductSchema()
        self.material_schema = MaterialSchema()
        self.work_center_schema = WorkCenterSchema()
        self.operation_schema = OperationSchema()
        self.asset_schema = AssetSchema()
        self.asset_group_schema = AssetGroupSchema()

    # =========================================================
    # Customer Logic
    # =========================================================

    def get_all_customers(self):
        return Customer.query.all()

    def get_customer_by_id(self, id):
        return Customer.query.get_or_404(id)

    def create_customer(self, data: dict) -> Customer:
        try:
            new_customer = self.customer_schema.load(data)
            db.session.add(new_customer)
            db.session.commit()
            return new_customer
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    def update_customer(self, id: int, data: dict) -> Customer:
        customer = self.get_customer_by_id(id)
        try:
            updated_customer = self.customer_schema.load(data, instance=customer, partial=True)
            db.session.commit()
            return updated_customer
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    def delete_customer(self, id: int):
        customer = self.get_customer_by_id(id)
        try:
            db.session.delete(customer)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    # =========================================================
    # Supplier Logic
    # =========================================================

    def get_all_suppliers(self):
        return Supplier.query.all()

    def create_supplier(self, data: dict) -> Supplier:
        try:
            new_supplier = self.supplier_schema.load(data)
            db.session.add(new_supplier)
            db.session.commit()
            return new_supplier
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    # =========================================================
    # Material & Product Logic
    # =========================================================

    def get_all_materials(self):
        return Material.query.all()

    def create_material(self, data: dict) -> Material:
        try:
            new_material = self.material_schema.load(data)
            db.session.add(new_material)
            db.session.commit()
            return new_material
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    def get_all_products(self):
        return Product.query.all()

    def create_product(self, data: dict) -> Product:
        try:
            new_product = self.product_schema.load(data)
            db.session.add(new_product)
            db.session.commit()
            return new_product
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    # --- Internal Product (Added) ---

    def get_all_internal_products(self):
        return InternalProduct.query.all()

    def create_internal_product(self, data: dict) -> InternalProduct:
        try:
            new_ip = self.internal_product_schema.load(data)
            db.session.add(new_ip)
            db.session.commit()
            return new_ip
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    # =========================================================
    # Resource Logic (WorkCenters, Operations, Assets)
    # =========================================================

    # --- Work Center ---
    def get_all_work_centers(self):
        return WorkCenter.query.all()

    def get_work_center_by_id(self, id):
        return WorkCenter.query.get_or_404(id)

    def create_work_center(self, data: dict) -> WorkCenter:
        try:
            new_wc = self.work_center_schema.load(data)
            db.session.add(new_wc)
            db.session.commit()
            return new_wc
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    # --- Operation ---
    def get_all_operations(self):
        return Operation.query.all()

    def create_operation(self, data: dict) -> Operation:
        try:
            new_op = self.operation_schema.load(data)
            db.session.add(new_op)
            db.session.commit()
            return new_op
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    # --- Asset ---
    def get_all_assets(self):
        return Asset.query.all()

    def create_asset(self, data: dict) -> Asset:
        try:
            new_asset = self.asset_schema.load(data)
            db.session.add(new_asset)
            db.session.commit()
            return new_asset
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    # --- Asset Group ---
    def get_all_asset_groups(self):
        return AssetGroup.query.all()

    def create_asset_group(self, data: dict) -> AssetGroup:
        try:
            new_group = self.asset_group_schema.load(data)
            db.session.add(new_group)
            db.session.commit()
            return new_group
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

# Singleton instance
md_service = MasterDataService()