# goji/app/process/models.py
from sqlalchemy import Sequence
from ..extensions import db
from ..models import ModelBase
from datetime import datetime

class Routing(ModelBase):
    """Defines the master record for a manufacturing process of a product."""
    id = db.Column(db.Integer, Sequence('gj_routing_id_seq'), primary_key=True)
    routing_status = db.Column(db.String(50), nullable=False, default='ACTIVE') # e.g., 'PLANNING', 'ACTIVE'
    int_product_id = db.Column(db.Integer, db.ForeignKey('gj_internal_products.id'), nullable=False)
    int_ver = db.Column(db.String(50), nullable=False)
    pcs_per_strip = db.Column(db.Integer)
    strips_per_panel = db.Column(db.Integer)
    is_default = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    
    
class RoutingOperation(ModelBase):
    """Defines a single step in a Routing."""
    id = db.Column(db.Integer, Sequence('gj_routing_operation_id_seq'), primary_key=True)
    routing_id = db.Column(db.Integer, db.ForeignKey('gj_routings.id'), nullable=False)
    operation_id = db.Column(db.Integer, db.ForeignKey('gj_operations.id'), nullable=False)
    step_num = db.Column(db.Integer, nullable=False)
    layer_def_id = db.Column(db.Integer, db.ForeignKey('gj_layer_definitions.id'), nullable=True)
    semi_part_num = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text)
    workpiece_pcs = db.Column(db.Numeric(10, 4))
    workpiece_len = db.Column(db.Numeric(10, 4))
    workpiece_width = db.Column(db.Numeric(10, 4))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

    
class LayerDefinition(ModelBase):
    """Master data for layer definitions (e.g., in PCB manufacturing)."""
    id = db.Column(db.Integer, Sequence('gj_layer_definition_id_seq'), primary_key=True)
    layer_code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    layer_name = db.Column(db.String(100))
    description = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

class LayerStructure(ModelBase):
    """Defines the hierarchical structure of layers for a product."""
    id = db.Column(db.Integer, Sequence('gj_layer_structure_id_seq'), primary_key=True)
    routing_id  = db.Column(db.Integer, db.ForeignKey('gj_routings.id'), nullable=False)
    current_layer_id = db.Column(db.Integer, db.ForeignKey('gj_layer_definitions.id'), nullable=True)
    next_layer_id = db.Column(db.Integer, db.ForeignKey('gj_layer_definitions.id'), nullable=False)
    is_primary_branch = db.Column(db.Boolean, nullable=False, default=False)
    hierarchy_level = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

    
class OperationResource(ModelBase):
    """Links a routing operation to a work center with specific time standards."""
    id = db.Column(db.Integer, Sequence('gj_operation_resource_id_seq'), primary_key=True)
    routing_op_id = db.Column(db.Integer, db.ForeignKey('gj_routing_operations.id'), nullable=False)
    wc_id = db.Column(db.Integer, db.ForeignKey('gj_work_centers.id'), nullable=False)
    setup_time_sec = db.Column(db.Integer, nullable=False, default=0)
    
    # --- ADDED: Raw measurement fields for flexible time input ---
    raw_run_time_val = db.Column(db.Numeric(12, 6))          # Original measured time value
    raw_run_time_uom = db.Column(db.String(20))              # Original measurement unit (e.g., 'min/pcs', 'sec/panel')
    items_per_raw_uom = db.Column(db.Integer)                # Conversion rate: number of items per raw UOM
    
    # --- Standardized field for planning engine ---
    run_time_sec_per_pc = db.Column(db.Numeric(12, 6), nullable=False)
    
    pref_level = db.Column(db.Integer, nullable=False, default=1)  # Priority level (1=preferred)
    is_active = db.Column(db.Boolean, nullable=False, default=True)  # Whether this resource option is active

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

   


class BomItem(ModelBase):
    """Defines a single material requirement for a routing operation."""
    id = db.Column(db.Integer, Sequence('gj_bom_item_id_seq'), primary_key=True)
    routing_op_id = db.Column(db.Integer, db.ForeignKey('gj_routing_operations.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('gj_materials.id'), nullable=False)
    
    # --- CORRECTED: Standardized BOM calculation fields ---
    quantity = db.Column(db.Numeric(12, 6), nullable=False)          # Numerator: input material quantity
    uom = db.Column(db.String(20), nullable=False)                   # Numerator: input material unit
    base_qty = db.Column(db.Numeric(12, 6), nullable=False, default=1)      # Denominator: output product base quantity
    base_uom = db.Column(db.String(20), nullable=False, default='pcs')      # Denominator: output product base unit
    multiplier = db.Column(db.Numeric(12, 6), nullable=False, default=1)    # Multiplier coefficient
    scrap_pct = db.Column(db.Numeric(5, 4), nullable=False, default=0)      # Scrap percentage (0-1 range)
    
    notes = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

    
class AlternateMaterial(ModelBase):
    """Defines an alternative material for a BomItem."""
    id = db.Column(db.Integer, Sequence('gj_alternate_material_id_seq'), primary_key=True)
    bom_item_id = db.Column(db.Integer, db.ForeignKey('gj_bom_items.id'), nullable=False)
    alt_material_id = db.Column(db.Integer, db.ForeignKey('gj_materials.id'), nullable=False)
    priority = db.Column(db.Integer, nullable=False, default=99)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
