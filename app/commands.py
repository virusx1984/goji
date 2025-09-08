# goji/app/commands.py
from flask.cli import with_appcontext
import click
from datetime import datetime, date

from .extensions import db

# Import all necessary models for a complete seed
from .user_management.models import *
from .organization.models import *
from .master_data.models import *
from .process.models import *
from .demand.models import *
from .system.models import *

@click.command(name='seed')
@with_appcontext
def seed_data_command():
    """Seeds the database with a complete initial set of data."""
    
    # --- Step 1: Clean up old data ---
    print("Clearing old data...")
    # Delete data in reverse order of creation to respect foreign key constraints
    # Note: Relationships are removed, so direct deletion is used.
    SalesOrderLine.query.delete()
    SalesOrder.query.delete()
    BomItem.query.delete()
    OperationResource.query.delete()
    RoutingOperation.query.delete()
    Routing.query.delete()
    Product.query.delete()
    Material.query.delete()
    WorkCenter.query.delete()
    Operation.query.delete()
    CustomerLocation.query.delete()
    Customer.query.delete()
    SupplierLocation.query.delete()
    Supplier.query.delete()
    # For association tables, we need to use delete() directly on the table object
    db.session.execute(user_roles.delete())
    db.session.execute(role_permissions.delete())
    Menu.query.delete()
    Plant.query.delete()
    FactoryCluster.query.delete()
    LegalEntity.query.delete()
    BusinessUnit.query.delete()
    Permission.query.delete()
    Role.query.delete()
    User.query.delete()
    db.session.commit()
    
    print("Old data cleared. Seeding new data...")

    # --- Step 2: Create Users, Roles, Permissions (Core Security) ---
    admin_user = User(username='admin', full_name='System Administrator', email='admin@goji.com', is_active=True)
    admin_user.set_password('supersecret')
    planner_user = User(username='planner1', full_name='Planner John', email='planner1@goji.com', is_active=True)
    planner_user.set_password('password123')
    db.session.add_all([admin_user, planner_user])
    db.session.commit()

    admin_role = Role(name='Administrator', description='Has all permissions')
    planner_role = Role(name='Planner', description='Responsible for capacity planning')
    
    # Create permissions
    permissions_data = [
        {'name': 'admin:all', 'description': 'Super administrator permission'},
        {'name': 'user:manage', 'description': 'Manage users and roles'},
        {'name': 'plan:view', 'description': 'View capacity plan'},
        {'name': 'routing:edit', 'description': 'Edit routings'},
    ]
    permissions = {}
    for p_data in permissions_data:
        perm = Permission(**p_data)
        permissions[p_data['name']] = perm
    db.session.add_all([admin_role, planner_role] + list(permissions.values()))
    db.session.commit()

    # Manually associate roles and permissions via the association table
    db.session.execute(role_permissions.insert().values(role_id=admin_role.id, permission_id=permissions['admin:all'].id))
    db.session.execute(role_permissions.insert().values(role_id=planner_role.id, permission_id=permissions['plan:view'].id))
    db.session.commit()

    # Manually associate users and roles via the association table
    db.session.execute(user_roles.insert().values(user_id=admin_user.id, role_id=admin_role.id))
    db.session.execute(user_roles.insert().values(user_id=planner_user.id, role_id=planner_role.id))
    db.session.commit()
    
    # --- Step 3: Create Organizational Structure ---
    bu_hdi = BusinessUnit(name='HDI', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    le_pengding = LegalEntity(name='鵬鼎', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    le_qingding = LegalEntity(name='慶鼎', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add_all([bu_hdi, le_pengding, le_qingding])
    db.session.commit()
    
    cluster_sz1 = FactoryCluster(name='深圳一園區', bu_id=bu_hdi.id, legal_entity_id=le_pengding.id, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    cluster_ha2 = FactoryCluster(name='淮安二園區', bu_id=bu_hdi.id, legal_entity_id=le_qingding.id, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add([cluster_sz1, cluster_ha2])
    db.session.commit()

    plant_sa03 = Plant(name='SA03', cluster_id=cluster_sz1.id, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    plant_sa02 = Plant(name='SA02', cluster_id=cluster_sz1.id, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    plant_hb04 = Plant(name='HB04', cluster_id=cluster_sz1.id, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add([plant_sa03, plant_sa02, plant_hb04])
    db.session.commit()

    # --- Step 4: Create Core Master Data for HDI PCB ---
    # Customer
    customer_apple = Customer(code='0001', name='H客戶', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    customer_byd = Customer(code='0002', name='比亞迪', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    customer_quanta = Customer(code='0003', name='廣達', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add([customer_apple, customer_byd])
    db.session.commit()

    location_byd_sz = CustomerLocation(cust_id=customer_byd.id, loc_name='Shenzhen', is_default=True, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    location_quanta_cq = CustomerLocation(cust_id=customer_quanta.id, loc_name='Chongqing', is_default=True, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add([location_byd_sz, location_quanta_cq])
    db.session.commit()

    # HDI PCB Product
    product_820_03902_A = Product(cust_id=customer_apple.id, end_cust_id = customer_apple.id, cust_part_num='820-03902-A',
                              description='3阶10层板', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    

    # layer definition
    layer_def_0 = LayerDefinition(layer_code='0', layer_name='外层', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    layer_def_34 = LayerDefinition(layer_code='34', layer_name='L04~05', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    layer_def_36 = LayerDefinition(layer_code='36', layer_name='L06~07', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    layer_def_143 = LayerDefinition(layer_code='143', layer_name='L03~08', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    layer_def_191 = LayerDefinition(layer_code='191', layer_name='L02~09', created_by_id=admin_user.id, updated_by_id=admin_user.id)

    db.session.add([layer_def_0, layer_def_34, layer_def_36, layer_def_143, layer_def_191])
    db.session.commit()

    # layer structures
    layer_struct_ = LayerStructure()


    # Suppliers
    supplier_tmc = Supplier(code='0001', name='台光', supplier_type='Manufacturer', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    supplier_tcf = Supplier(code='0002', name='台湾铜箔', supplier_type='Manufacturer', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    
    db.session.add_all([supplier_tmc, supplier_tcf])
    db.session.commit()
    
    ccl_location = SupplierLocation(supplier_id=supplier_tmc.id, loc_name='中山', is_default=True, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    cu_location = SupplierLocation(supplier_id=supplier_tcf.id, loc_name='台北', is_default=True, created_by_id=admin_user.id, updated_by_id=admin_user.id)

    db.session.add_all([ccl_location, cu_location])
    db.session.commit()

    # Operations
    op_cutting = Operation(code='0001', name='裁板', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_layer_pre_treatment = Operation(code='0002', name='线路前处理', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_ldi = Operation(code='0003', name='LDI', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_des = Operation(code='0004', name='DES', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_aoi = Operation(code='0005', name='AOI', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_vrs = Operation(code='0006', name='VRS', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_brown_oxide = Operation(code='0007', name='棕化', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_layup = Operation(code='0008', name='叠板', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_lamination = Operation(code='0009', name='压合', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_x_ray = Operation(code='0010', name='X-Ray钻靶', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_lam_post_treatment = Operation(code='0011', name='压合后处理', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_black_oxide = Operation(code='0012', name='黑化', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_laser_drilling = Operation(code='0013', name='镭射钻孔', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_plasma = Operation(code='0014', name='Plasma', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_mechanical_drilling = Operation(code='0015', name='机械钻孔', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_plating_pre_treatment = Operation(code='0016', name='电镀前处理', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_horizontal_plating = Operation(code='0017', name='水平电镀', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_vcp = Operation(code='0018', name='VCP电镀', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_sm_pre_treatment = Operation(code='0019', name='防焊前处理', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_printing = Operation(code='0020', name='印刷', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_di = Operation(code='0021', name='DI曝光', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_sm_developing = Operation(code='0022', name='防焊显影', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_sm_post_baking = Operation(code='0023', name='防焊后烤', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_enig_pre_treatment = Operation(code='0024', name='化金前处理', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_enig_lamination = Operation(code='0025', name='化金压膜', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_enig_exposure = Operation(code='0026', name='化金曝光', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_enig = Operation(code='0027', name='浸镍金', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_enig_developing = Operation(code='0028', name='化金显影', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_enig_striping = Operation(code='0029', name='化金去膜', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_routing = Operation(code='0030', name='捞型', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_4w_testing = Operation(code='0031', name='四线测试', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_avi = Operation(code='0032', name='AVI检查', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_packing = Operation(code='0033', name='包装', created_by_id=admin_user.id, updated_by_id=admin_user.id)

    db.session.add_all([
        op_cutting,
        op_layer_pre_treatment,
        op_ldi,
        op_des,
        op_aoi,
        op_vrs,
        op_brown_oxide,
        op_layup,
        op_lamination,
        op_x_ray,
        op_lam_post_treatment,
        op_black_oxide,
        op_laser_drilling,
        op_plasma,
        op_mechanical_drilling,
        op_plating_pre_treatment,
        op_horizontal_plating,
        op_vcp,
        op_sm_pre_treatment,
        op_printing,
        op_di,
        op_sm_developing,
        op_sm_post_baking,
        op_enig_pre_treatment,
        op_enig_lamination,
        op_enig_exposure,
        op_enig,
        op_enig_developing,
        op_enig_striping,
        op_routing,
        op_4w_testing,
        op_avi,
        op_packing
    ])
    db.session.commit()
    
    
    # Work Centers
    wc_imaging = WorkCenter(plant_id=default_plant.id, name='LDI Imaging Line', daily_avail_sec=28800, oee_pct=0.85, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    wc_etching = WorkCenter(plant_id=default_plant.id, name='Etching Department', daily_avail_sec=25200, oee_pct=0.80, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    wc_lamination = WorkCenter(plant_id=default_plant.id, name='Lamination Press', daily_avail_sec=21600, oee_pct=0.75, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    wc_drilling = WorkCenter(plant_id=default_plant.id, name='Laser Drill Center', daily_avail_sec=32400, oee_pct=0.90, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    wc_plating = WorkCenter(plant_id=default_plant.id, name='Plating Line', daily_avail_sec=28800, oee_pct=0.82, created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # Materials
    mat_cu_foil = Material(part_num='RAW-CU-18UM', material_type='RAW', name='18Î¼m Copper Foil', uom='SQMT', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    mat_fr4 = Material(part_num='RAW-FR4-0.2', material_type='RAW', name='FR4 0.2mm Core', uom='SQMT', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    mat_prepreg = Material(part_num='RAW-PP-1080', material_type='RAW', name='1080 Prepreg', uom='SQMT', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    mat_chemicals = Material(part_num='RAW-CHEM-ETCH', material_type='RAW', name='Etching Chemicals', uom='L', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    
    
    
    db.session.add_all([apple_location, cu_location, fr4_location, op_imaging, op_etching, op_lamination, 
                       op_drilling, op_plating, wc_imaging, wc_etching, wc_lamination, wc_drilling, 
                       wc_plating, mat_cu_foil, mat_fr4, mat_prepreg, mat_chemicals, product_hdi_pcb])
    db.session.commit()

    # --- Step 5: Create HDI PCB Process Data (Routing) ---
    routing_hdi = Routing(product_id=product_hdi_pcb.id, plant_id=default_plant.id, int_part_num='HDI-6L-A12', 
                         int_ver='B', is_default=True, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(routing_hdi)
    db.session.commit()

    # Step 10: LDI Imaging
    ro_10 = RoutingOperation(routing_id=routing_hdi.id, operation_id=op_imaging.id, step_num=10, 
                            created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(ro_10)
    db.session.commit()
    res_10 = OperationResource(routing_op_id=ro_10.id, wc_id=wc_imaging.id, 
                              run_time_sec_per_pc=120,
                              raw_run_time_val=2.0,          # 2.0 minutes per panel
                              raw_run_time_uom='min/panel',  # Original measurement unit
                              items_per_raw_uom=1,           # 1 panel per measurement
                              created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # Step 20: Copper Etching
    ro_20 = RoutingOperation(routing_id=routing_hdi.id, operation_id=op_etching.id, step_num=20, 
                            created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(ro_20)
    db.session.commit()
    res_20 = OperationResource(routing_op_id=ro_20.id, wc_id=wc_etching.id, 
                              run_time_sec_per_pc=180,
                              raw_run_time_val=3.0,          # 3.0 minutes per panel
                              raw_run_time_uom='min/panel',  # Original measurement unit
                              items_per_raw_uom=1,           # 1 panel per measurement
                              created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # Step 30: Multi-layer Lamination
    ro_30 = RoutingOperation(routing_id=routing_hdi.id, operation_id=op_lamination.id, step_num=30, 
                            created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(ro_30)
    db.session.commit()
    res_30 = OperationResource(routing_op_id=ro_30.id, wc_id=wc_lamination.id, 
                              run_time_sec_per_pc=900,
                              raw_run_time_val=15.0,         # 15.0 minutes per panel
                              raw_run_time_uom='min/panel',  # Original measurement unit
                              items_per_raw_uom=1,           # 1 panel per measurement
                              created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # Step 40: Laser Drilling
    ro_40 = RoutingOperation(routing_id=routing_hdi.id, operation_id=op_drilling.id, step_num=40, 
                            created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(ro_40)
    db.session.commit()
    res_40 = OperationResource(routing_op_id=ro_40.id, wc_id=wc_drilling.id, 
                              run_time_sec_per_pc=300,
                              raw_run_time_val=5.0,          # 5.0 minutes per panel
                              raw_run_time_uom='min/panel',  # Original measurement unit
                              items_per_raw_uom=1,           # 1 panel per measurement
                              created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # Step 50: Copper Plating
    ro_50 = RoutingOperation(routing_id=routing_hdi.id, operation_id=op_plating.id, step_num=50, 
                            created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(ro_50)
    db.session.commit()
    res_50 = OperationResource(routing_op_id=ro_50.id, wc_id=wc_plating.id, 
                              run_time_sec_per_pc=480,
                              raw_run_time_val=8.0,          # 8.0 minutes per panel
                              raw_run_time_uom='min/panel',  # Original measurement unit
                              items_per_raw_uom=1,           # 1 panel per measurement
                              created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # BOM Items with new calculation fields
    bom_10 = BomItem(routing_op_id=ro_10.id, material_id=mat_cu_foil.id, quantity=0.8, uom='SQMT',
                    base_qty=1, base_uom='panel', multiplier=1, scrap_pct=0.08,  # 8% scrap for imaging
                    created_by_id=admin_user.id, updated_by_id=admin_user.id)

    bom_20 = BomItem(routing_op_id=ro_20.id, material_id=mat_chemicals.id, quantity=2.5, uom='L',
                    base_qty=1, base_uom='panel', multiplier=1, scrap_pct=0.05,  # 5% scrap for etching
                    created_by_id=admin_user.id, updated_by_id=admin_user.id)

    bom_30 = BomItem(routing_op_id=ro_30.id, material_id=mat_fr4.id, quantity=0.6, uom='SQMT',
                    base_qty=1, base_uom='panel', multiplier=1, scrap_pct=0.03,  # 3% scrap for lamination
                    created_by_id=admin_user.id, updated_by_id=admin_user.id)

    bom_40 = BomItem(routing_op_id=ro_40.id, material_id=mat_prepreg.id, quantity=0.4, uom='SQMT',
                    base_qty=1, base_uom='panel', multiplier=1, scrap_pct=0.02,  # 2% scrap for drilling
                    created_by_id=admin_user.id, updated_by_id=admin_user.id)

    db.session.add_all([res_10, res_20, res_30, res_40, res_50, bom_10, bom_20, bom_30, bom_40])
    db.session.commit()

    # --- Step 6: Create Demand Data (Sales Order) ---
    # FIX: Added a unique order_num for SalesOrder
    so_apple = SalesOrder(order_num='SO-2025-HDI001', cust_id=customer_apple.id, ship_to_loc_id=apple_location.id, 
                         order_date=date.today(), 
                         created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(so_apple)
    db.session.commit()

    sol_1 = SalesOrderLine(order_id=so_apple.id, line_num=1, product_id=product_hdi_pcb.id, 
                          quantity=1000, routing_id=routing_hdi.id, 
                          created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(sol_1)
    db.session.commit()

    print("Database seeded successfully!")
    print("Sample login: admin/supersecret or planner1/password123")

