# goji/app/master_data/models.py
from ..extensions import db
from ..models import ModelBase
from datetime import datetime

# =============================================
# External Entities Domain
# =============================================

class Customer(ModelBase):
    """
    Stores customer's legal/group information (Bill-To).
    """
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    
    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

    # Relationships
    locations = db.relationship('CustomerLocation', backref='customer', lazy='dynamic', cascade="all, delete-orphan")
    products = db.relationship('Product', backref='customer', lazy='dynamic')

class CustomerLocation(ModelBase):
    """
    Stores customer's physical delivery locations (Ship-To).
    """
    id = db.Column(db.Integer, primary_key=True)
    cust_id = db.Column(db.Integer, db.ForeignKey('gj_customers.id'), nullable=False)
    loc_name = db.Column(db.String(255), nullable=False)
    loc_code = db.Column(db.String(50))
    address = db.Column(db.String(500))
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    is_default = db.Column(db.Boolean, nullable=False, default=False)

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

class Supplier(ModelBase):
    """
    Stores supplier's legal/group information.
    """
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    supplier_type = db.Column(db.String(50)) # e.g., 'Manufacturer', 'Distributor'

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

    # Relationships
    locations = db.relationship('SupplierLocation', backref='supplier', lazy='dynamic', cascade="all, delete-orphan")

    # --- ADDED: Relationships for supplier-to-supplier connections ---
    # Relationships where this supplier is the agent/subsidiary
    manufacturers = db.relationship(
        'SupplierRelationship', 
        foreign_keys='SupplierRelationship.supplier_id',
        backref='agent_supplier',
        lazy='dynamic'
    )
    # Relationships where this supplier is the manufacturer/parent
    agents = db.relationship(
        'SupplierRelationship', 
        foreign_keys='SupplierRelationship.mfg_id',
        backref='manufacturer_supplier',
        lazy='dynamic'
    )

class SupplierLocation(ModelBase):
    """
    Stores supplier's physical shipping/service locations.
    """
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('gj_suppliers.id'), nullable=False)
    loc_name = db.Column(db.String(255), nullable=False)
    loc_code = db.Column(db.String(50))
    address = db.Column(db.String(500))
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    is_default = db.Column(db.Boolean, nullable=False, default=False)
    
    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

    # --- CHANGED: Relationship points to the correctly named 'MaterialSupplier' class ---
    materials_supplied = db.relationship('MaterialSupplier', backref='supplier_location', lazy='dynamic', cascade="all, delete-orphan")

# =============================================
# Item & Resource Domain
# =============================================

class Product(ModelBase):
    """
    Defines a product required by a customer. This is the root for a routing.
    """
    id = db.Column(db.Integer, primary_key=True)
    product_status = db.Column(db.String(50), nullable=False, default='ACTIVE') # 'PLANNING', 'ACTIVE', 'EOL'
    ref_product_id = db.Column(db.Integer, db.ForeignKey('gj_products.id'), nullable=True)
    cust_id = db.Column(db.Integer, db.ForeignKey('gj_customers.id'), nullable=False)
    cust_part_num = db.Column(db.String(100), nullable=False, index=True)
    cust_ver = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500))
    pcs_per_strip = db.Column(db.Integer)
    strips_per_panel = db.Column(db.Integer)

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

class Material(ModelBase):
    """
    Master data for all items (raw, semi-finished, finished goods).
    """
    id = db.Column(db.Integer, primary_key=True)
    part_num = db.Column(db.String(100), nullable=False, unique=True, index=True)
    material_type = db.Column(db.String(50), nullable=False) # 'RAW', 'SEMI', 'FINISHED'
    name = db.Column(db.String(255))
    description = db.Column(db.String(500))
    uom = db.Column(db.String(20), nullable=False) # Unit of Measure
    length = db.Column(db.Numeric(10, 4))
    width = db.Column(db.Numeric(10, 4))
    thickness = db.Column(db.Numeric(10, 4))

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

    # --- CHANGED: Relationship points to the correctly named 'MaterialSupplier' class ---
    suppliers = db.relationship('MaterialSupplier', backref='material', lazy='dynamic', cascade="all, delete-orphan")

class Operation(ModelBase):
    """
    Standard, reusable manufacturing operations.
    """
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(500))

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

class Asset(ModelBase):
    """
    Master data for physical assets (equipment, tools, etc.).
    """
    id = db.Column(db.Integer, primary_key=True)
    asset_group_id = db.Column(db.Integer, db.ForeignKey('gj_asset_groups.id'), nullable=True)
    asset_tag = db.Column(db.String(100), nullable=False, unique=True)
    serial_num = db.Column(db.String(100), unique=True)
    model_num = db.Column(db.String(100))
    sup_loc_id = db.Column(db.Integer, db.ForeignKey('gj_supplier_locations.id'))
    mfg_id = db.Column(db.Integer, db.ForeignKey('gj_suppliers.id'))
    purchase_date = db.Column(db.Date)
    install_date = db.Column(db.Date)
    asset_status = db.Column(db.String(50), nullable=False, default='Active')

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

    # Relationships to match AssetSchema
    asset_group = db.relationship('AssetGroup', backref='assets', lazy=True)
    supplier_location = db.relationship('SupplierLocation', foreign_keys=[sup_loc_id], lazy=True)
    manufacturer = db.relationship('Supplier', foreign_keys=[mfg_id], lazy=True)

class AssetGroup(ModelBase):
    """
    A logical grouping of assets (e.g., a production line).
    """
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('gj_plants.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, unique=True)
    group_status = db.Column(db.String(50), nullable=False, default='Active')
    description = db.Column(db.String(500))

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

class WorkCenter(ModelBase):
    """
    A logical scheduling unit for capacity planning.
    """
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('gj_plants.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(500))
    daily_avail_sec = db.Column(db.Integer, nullable=False)
    oee_pct = db.Column(db.Numeric(5, 4), nullable=False)

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

    # Relationship for Work Centers and Assets (Many-to-Many)
    assets = db.relationship(
        'Asset', 
        secondary='gj_work_center_assets', 
        backref=db.backref('work_centers', lazy='dynamic'), 
        lazy='dynamic'
    )

# --- Association Table for Work Centers and Assets ---
work_center_assets = db.Table('gj_work_center_assets',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('wc_id', db.Integer, db.ForeignKey('gj_work_centers.id'), nullable=False),
    db.Column('asset_id', db.Integer, db.ForeignKey('gj_assets.id'), nullable=False),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False),
    db.Column('created_by_id', db.Integer, db.ForeignKey('gj_users.id'))
)

# --- RENAMED: This class now correctly represents the 'material_suppliers' table ---
class MaterialSupplier(ModelBase):
    """
    Association object linking a Material to a SupplierLocation.
    This corresponds to the 'material_suppliers' table in the design doc.
    """
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('gj_materials.id'), nullable=False)
    sup_loc_id = db.Column(db.Integer, db.ForeignKey('gj_supplier_locations.id'), nullable=False)
    
    # Additional attributes of the relationship
    supplier_part_num = db.Column(db.String(100))  # The part number used by the supplier
    is_preferred = db.Column(db.Boolean, nullable=False, default=False)  # Is this the preferred source?

    # --- ADDED: Procurement and pricing fields ---
    lead_time_days = db.Column(db.Integer)  # Procurement lead time in days
    unit_price = db.Column(db.Numeric(12, 6))  # Purchase unit price
    min_order_qty = db.Column(db.Numeric(12, 4))  # Minimum order quantity (MOQ)
    currency = db.Column(db.String(3), default='USD')  # Currency code for pricing

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

    # Unique constraint to prevent duplicate entries for the same material-supplier pair
    __table_args__ = (db.UniqueConstraint('material_id', 'sup_loc_id', name='uq_material_supplier_loc'),)


# --- ADDED: The missing 'supplier_relationships' model ---
class SupplierRelationship(ModelBase):
    """
    Defines relationships between suppliers (e.g., agent, parent company).
    This corresponds to the 'supplier_relationships' table in the design doc.
    """
    id = db.Column(db.Integer, primary_key=True)
    # This is the agent or subsidiary supplier
    supplier_id = db.Column(db.Integer, db.ForeignKey('gj_suppliers.id'), nullable=False)
    # This is the manufacturer or parent company supplier
    mfg_id = db.Column(db.Integer, db.ForeignKey('gj_suppliers.id'), nullable=False)
    relation_type = db.Column(db.String(50), nullable=False) # e.g., 'Agent', 'Group Member'

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
