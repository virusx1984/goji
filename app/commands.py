# goji/app/commands.py
from flask.cli import with_appcontext
import click
from datetime import datetime, date

from .extensions import db

# Import all necessary models for a complete seed
from .user_management.models import User, Role, Permission, Menu, user_roles, role_permissions
from .organization.models import Plant, BusinessUnit, LegalEntity, FactoryCluster
from .master_data.models import Customer, CustomerLocation, Supplier, SupplierLocation, Product, Material, Operation, WorkCenter
from .process.models import Routing, RoutingOperation, OperationResource, BomItem
from .demand.models import SalesOrder, SalesOrderLine


@click.command(name='seed')
@with_appcontext
def seed_data_command():
    """Seeds the database with a complete set of initial data for HDI PCB manufacturing demonstration."""
    
    # --- Step 1: Clean up old data ---
    print("Clearing old data...")
    # Delete data in reverse order of creation to respect foreign key constraints
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
    
    print("Old data cleared. Seeding new HDI PCB manufacturing data...")

    # --- Step 2: Create Users, Roles, Permissions (Core Security) ---
    admin_user = User(username='admin', full_name='System Administrator', email='admin@goji.com', is_active=True)
    admin_user.set_password('supersecret')
    planner_user = User(username='planner1', full_name='Planner John', email='planner1@goji.com', is_active=True)
    planner_user.set_password('password123')
    db.session.add_all([admin_user, planner_user])
    db.session.commit()

    admin_role = Role(name='Administrator', description='Has all permissions')
    planner_role = Role(name='Planner', description='Responsible for capacity planning')
    permissions_data = [
        {'name': 'admin:all', 'description': 'Super administrator permission'},
        {'name': 'user:manage', 'description': 'Manage users and roles'},
        {'name': 'plan:view', 'description': 'View capacity plan'},
        {'name': 'routing:edit', 'description': 'Edit routings'},
    ]
    permissions = {p['name']: Permission(**p) for p in permissions_data}
    db.session.add_all([admin_role, planner_role] + list(permissions.values()))
    db.session.commit()

    admin_role.permissions.append(permissions['admin:all'])
    planner_role.permissions.append(permissions['plan:view'])
    admin_user.roles.append(admin_role)
    planner_user.roles.append(planner_role)
    
    # --- Step 3: Create Organizational Structure ---
    default_bu = BusinessUnit(name='PCB Manufacturing BU', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    default_le = LegalEntity(name='Goji Electronics Ltd.', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add_all([default_bu, default_le])
    db.session.commit()
    
    default_cluster = FactoryCluster(name='HDI Production Cluster', business_unit=default_bu, legal_entity=default_le, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(default_cluster)
    db.session.commit()

    default_plant = Plant(name='Shenzhen HDI Plant', factory_cluster=default_cluster, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(default_plant)
    db.session.commit()

    # --- Step 4: Create Core Master Data for HDI PCB ---
    # Customer
    customer_apple = Customer(code='CUST-APPLE', name='Apple Inc.', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(customer_apple)
    db.session.commit()
    apple_location = CustomerLocation(customer=customer_apple, loc_name='Cupertino HQ', is_default=True, created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # Suppliers
    supplier_cu = Supplier(code='SUP-CUFOIL', name='Copper Foil Inc.', supplier_type='Manufacturer', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    supplier_fr4 = Supplier(code='SUP-FR4', name='FR4 Materials Co.', supplier_type='Manufacturer', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add_all([supplier_cu, supplier_fr4])
    db.session.commit()
    
    cu_location = SupplierLocation(supplier=supplier_cu, loc_name='Main Factory', is_default=True, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    fr4_location = SupplierLocation(supplier=supplier_fr4, loc_name='Production Hub', is_default=True, created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # Operations
    op_imaging = Operation(code='OP-10', name='LDI Imaging', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_etching = Operation(code='OP-20', name='Copper Etching', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_lamination = Operation(code='OP-30', name='Multi-layer Lamination', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_drilling = Operation(code='OP-40', name='Laser Drilling', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_plating = Operation(code='OP-50', name='Copper Plating', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    
    # Work Centers
    wc_imaging = WorkCenter(plant=default_plant, name='LDI Imaging Line', daily_avail_sec=28800, oee_pct=0.85, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    wc_etching = WorkCenter(plant=default_plant, name='Etching Department', daily_avail_sec=25200, oee_pct=0.80, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    wc_lamination = WorkCenter(plant=default_plant, name='Lamination Press', daily_avail_sec=21600, oee_pct=0.75, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    wc_drilling = WorkCenter(plant=default_plant, name='Laser Drill Center', daily_avail_sec=32400, oee_pct=0.90, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    wc_plating = WorkCenter(plant=default_plant, name='Plating Line', daily_avail_sec=28800, oee_pct=0.82, created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # Materials
    mat_cu_foil = Material(part_num='RAW-CU-18UM', material_type='RAW', name='18μm Copper Foil', uom='SQMT', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    mat_fr4 = Material(part_num='RAW-FR4-0.2', material_type='RAW', name='FR4 0.2mm Core', uom='SQMT', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    mat_prepreg = Material(part_num='RAW-PP-1080', material_type='RAW', name='1080 Prepreg', uom='SQMT', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    mat_chemicals = Material(part_num='RAW-CHEM-ETCH', material_type='RAW', name='Etching Chemicals', uom='L', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    
    # HDI PCB Product
    product_hdi_pcb = Product(customer=customer_apple, cust_part_num='A12-HDI-6L', cust_ver='B', 
                             description='6-Layer HDI PCB for A12 Chip', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    
    db.session.add_all([apple_location, cu_location, fr4_location, op_imaging, op_etching, op_lamination, 
                       op_drilling, op_plating, wc_imaging, wc_etching, wc_lamination, wc_drilling, 
                       wc_plating, mat_cu_foil, mat_fr4, mat_prepreg, mat_chemicals, product_hdi_pcb])
    db.session.commit()

    # --- Step 5: Create HDI PCB Process Data (Routing) ---
    routing_hdi = Routing(product=product_hdi_pcb, plant=default_plant, int_part_num='HDI-6L-A12', 
                         int_ver='B', is_default=True, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(routing_hdi)
    db.session.commit()

    # Step 10: LDI Imaging
    ro_10 = RoutingOperation(routing=routing_hdi, operation=op_imaging, step_num=10, 
                            created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(ro_10)
    db.session.commit()
    res_10 = OperationResource(routing_operation=ro_10, work_center=wc_imaging, 
                              run_time_sec_per_pc=120,
                              raw_run_time_val=2.0,          # 2.0 minutes per panel
                              raw_run_time_uom='min/panel',  # Original measurement unit
                              items_per_raw_uom=1,           # 1 panel per measurement
                              created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # Step 20: Copper Etching
    ro_20 = RoutingOperation(routing=routing_hdi, operation=op_etching, step_num=20, 
                            created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(ro_20)
    db.session.commit()
    res_20 = OperationResource(routing_operation=ro_20, work_center=wc_etching, 
                              run_time_sec_per_pc=180,
                              raw_run_time_val=3.0,          # 3.0 minutes per panel
                              raw_run_time_uom='min/panel',  # Original measurement unit
                              items_per_raw_uom=1,           # 1 panel per measurement
                              created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # Step 30: Multi-layer Lamination
    ro_30 = RoutingOperation(routing=routing_hdi, operation=op_lamination, step_num=30, 
                            created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(ro_30)
    db.session.commit()
    res_30 = OperationResource(routing_operation=ro_30, work_center=wc_lamination, 
                              run_time_sec_per_pc=900,
                              raw_run_time_val=15.0,         # 15.0 minutes per panel
                              raw_run_time_uom='min/panel',  # Original measurement unit
                              items_per_raw_uom=1,           # 1 panel per measurement
                              created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # Step 40: Laser Drilling
    ro_40 = RoutingOperation(routing=routing_hdi, operation=op_drilling, step_num=40, 
                            created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(ro_40)
    db.session.commit()
    res_40 = OperationResource(routing_operation=ro_40, work_center=wc_drilling, 
                              run_time_sec_per_pc=300,
                              raw_run_time_val=5.0,          # 5.0 minutes per panel
                              raw_run_time_uom='min/panel',  # Original measurement unit
                              items_per_raw_uom=1,           # 1 panel per measurement
                              created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # Step 50: Copper Plating
    ro_50 = RoutingOperation(routing=routing_hdi, operation=op_plating, step_num=50, 
                            created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(ro_50)
    db.session.commit()
    res_50 = OperationResource(routing_operation=ro_50, work_center=wc_plating, 
                              run_time_sec_per_pc=480,
                              raw_run_time_val=8.0,          # 8.0 minutes per panel
                              raw_run_time_uom='min/panel',  # Original measurement unit
                              items_per_raw_uom=1,           # 1 panel per measurement
                              created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # BOM Items with new calculation fields
    bom_10 = BomItem(routing_operation=ro_10, material=mat_cu_foil, quantity=0.8, uom='SQMT',
                    base_qty=1, base_uom='panel', multiplier=1, scrap_pct=0.08,  # 8% scrap for imaging
                    created_by_id=admin_user.id, updated_by_id=admin_user.id)

    bom_20 = BomItem(routing_operation=ro_20, material=mat_chemicals, quantity=2.5, uom='L',
                    base_qty=1, base_uom='panel', multiplier=1, scrap_pct=0.05,  # 5% scrap for etching
                    created_by_id=admin_user.id, updated_by_id=admin_user.id)

    bom_30 = BomItem(routing_operation=ro_30, material=mat_fr4, quantity=0.6, uom='SQMT',
                    base_qty=1, base_uom='panel', multiplier=1, scrap_pct=0.03,  # 3% scrap for lamination
                    created_by_id=admin_user.id, updated_by_id=admin_user.id)

    bom_40 = BomItem(routing_operation=ro_40, material=mat_prepreg, quantity=0.4, uom='SQMT',
                    base_qty=1, base_uom='panel', multiplier=1, scrap_pct=0.02,  # 2% scrap for drilling
                    created_by_id=admin_user.id, updated_by_id=admin_user.id)

    db.session.add_all([res_10, res_20, res_30, res_40, res_50, bom_10, bom_20, bom_30, bom_40])
    db.session.commit()

    # --- Step 6: Create Demand Data (Sales Order) ---
    so_apple = SalesOrder(order_num='SO-2025-HDI001', customer=customer_apple, 
                         ship_to_location=apple_location, order_date=date.today(), 
                         created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(so_apple)
    db.session.commit()

    sol_1 = SalesOrderLine(sales_order=so_apple, line_num=1, product=product_hdi_pcb, 
                          quantity=1000, routing=routing_hdi, 
                          created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(sol_1)
    db.session.commit()

    print("Database seeded successfully with HDI PCB manufacturing demonstration data!")
    print("Sample login: admin/supersecret or planner1/password123")
