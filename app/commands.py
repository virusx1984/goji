# goji/app/commands.py
from flask.cli import with_appcontext
import click
from datetime import datetime, date

from .extensions import db

# --- CHANGE: Import all necessary models for a complete seed ---
from .user_management.models import User, Role, Permission, Menu, user_roles, role_permissions
from .organization.models import Plant, BusinessUnit, LegalEntity, FactoryCluster
from .master_data.models import Customer, CustomerLocation, Supplier, SupplierLocation, Product, Material, Operation, WorkCenter
from .process.models import Routing, RoutingOperation, OperationResource, BomItem
from .demand.models import SalesOrder, SalesOrderLine


@click.command(name='seed')
@with_appcontext
def seed_data_command():
    """Seeds the database with a complete set of initial data for demonstration."""
    
    # --- Step 1: Clean up old data ---
    print("Clearing old data...")
    # In reverse order of creation to respect foreign key constraints
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
    default_bu = BusinessUnit(name='Default BU', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    default_le = LegalEntity(name='Default Legal Entity', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add_all([default_bu, default_le])
    db.session.commit()
    
    default_cluster = FactoryCluster(name='Default Cluster', business_unit=default_bu, legal_entity=default_le, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(default_cluster)
    db.session.commit()

    default_plant = Plant(name='Default Plant', factory_cluster=default_cluster, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(default_plant)
    db.session.commit()

    # --- Step 4: Create Core Master Data ---
    customer_acme = Customer(code='CUST-ACME', name='ACME Corporation', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(customer_acme)
    db.session.commit()
    acme_location = CustomerLocation(customer=customer_acme, loc_name='Main Warehouse', is_default=True, created_by_id=admin_user.id, updated_by_id=admin_user.id)

    supplier_parts = Supplier(code='SUP-PARTS', name='Global Parts Inc.', supplier_type='Distributor', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(supplier_parts)
    db.session.commit()
    parts_location = SupplierLocation(supplier=supplier_parts, loc_name='Main Hub', is_default=True, created_by_id=admin_user.id, updated_by_id=admin_user.id)

    op_cutting = Operation(code='OP-10', name='Cutting', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    op_assembly = Operation(code='OP-20', name='Assembly', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    
    wc_cutting = WorkCenter(plant=default_plant, name='Cutting Center', daily_avail_sec=28800, oee_pct=0.85, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    wc_assembly = WorkCenter(plant=default_plant, name='Assembly Line 1', daily_avail_sec=28800, oee_pct=0.90, created_by_id=admin_user.id, updated_by_id=admin_user.id)

    mat_raw = Material(part_num='RAW-STEEL-01', material_type='RAW', name='Steel Plate', uom='KG', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    mat_semi = Material(part_num='SEMI-BRACKET-A', material_type='SEMI', name='Bracket Assembly', uom='PCS', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    
    product_widget = Product(customer=customer_acme, cust_part_num='WIDGET-1000', cust_ver='A', description='Standard Widget', created_by_id=admin_user.id, updated_by_id=admin_user.id)
    
    db.session.add_all([acme_location, parts_location, op_cutting, op_assembly, wc_cutting, wc_assembly, mat_raw, mat_semi, product_widget])
    db.session.commit()

    # --- Step 5: Create Process Data (Routing) ---
    routing_widget = Routing(product=product_widget, plant=default_plant, int_part_num='INTERNAL-WIDGET-1000', int_ver='A', is_default=True, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(routing_widget)
    db.session.commit()

    # Step 10: Cutting
    ro_10 = RoutingOperation(routing=routing_widget, operation=op_cutting, step_num=10, semi_part_num=mat_semi.part_num, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(ro_10)
    db.session.commit()
    res_10 = OperationResource(routing_operation=ro_10, work_center=wc_cutting, run_time_sec_per_pc=15, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    bom_10 = BomItem(routing_operation=ro_10, material=mat_raw, quantity=0.5, uom='KG', created_by_id=admin_user.id, updated_by_id=admin_user.id)

    # Step 20: Assembly
    ro_20 = RoutingOperation(routing=routing_widget, operation=op_assembly, step_num=20, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(ro_20)
    db.session.commit()
    res_20 = OperationResource(routing_operation=ro_20, work_center=wc_assembly, run_time_sec_per_pc=45, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    bom_20 = BomItem(routing_operation=ro_20, material=mat_semi, quantity=1, uom='PCS', created_by_id=admin_user.id, updated_by_id=admin_user.id)

    db.session.add_all([res_10, bom_10, res_20, bom_20])
    db.session.commit()

    # --- Step 6: Create Demand Data (Sales Order) ---
    so_acme = SalesOrder(order_num='SO-2025-001', customer=customer_acme, ship_to_location=acme_location, order_date=date.today(), created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(so_acme)
    db.session.commit()

    sol_1 = SalesOrderLine(sales_order=so_acme, line_num=1, product=product_widget, quantity=100, routing=routing_widget, created_by_id=admin_user.id, updated_by_id=admin_user.id)
    db.session.add(sol_1)
    db.session.commit()

    print("Database seeded successfully with demonstration data!")
