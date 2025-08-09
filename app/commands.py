# goji/app/commands.py
from flask.cli import with_appcontext
import click
from .extensions import db
from .models import (
    User, 
    Role, 
    Permission, 
    Menu, 
    Plant, 
    BusinessUnit, 
    LegalEntity,
    FactoryCluster,
    user_roles, 
    role_permissions
)

@click.command(name='seed')
@with_appcontext
def seed_data_command():
    """Seeds the database with initial data for core models."""
    print("Clearing old data...")
    # Clean up old data in a specific order to respect foreign key constraints
    # Delete association table contents first
    db.session.execute(user_roles.delete())
    db.session.execute(role_permissions.delete())
    
    # Delete models that depend on others first
    Menu.query.delete()
    Plant.query.delete()
    FactoryCluster.query.delete()
    LegalEntity.query.delete()
    BusinessUnit.query.delete()
    
    # Finally, delete the core permission models
    Permission.query.delete()
    Role.query.delete()
    User.query.delete()
    
    db.session.commit()
    print("Old data cleared. Seeding new data...")

    # --- 1. Create Users ---
    admin_user = User(
        username='admin', 
        full_name='System Administrator', 
        email='admin@goji.com', 
        is_active=True
    )
    admin_user.set_password('supersecret')
    
    planner_user = User(
        username='planner1', 
        full_name='Planner John', 
        email='planner1@goji.com', 
        is_active=True
    )
    planner_user.set_password('password123')
    db.session.add_all([admin_user, planner_user])
    # We need to commit users first to get the admin_user.id for audit fields
    db.session.commit()

    # --- 2. Create Roles ---
    admin_role = Role(name='Administrator', description='Has all permissions')
    planner_role = Role(name='Planner', description='Responsible for capacity planning')
    viewer_role = Role(name='Viewer', description='Read-only access')
    
    # --- 3. Create Permissions ---
    permissions_data = [
        {'name': 'admin:all', 'description': 'Super administrator permission (grant all access)'},
        {'name': 'user:manage', 'description': 'Manage users, roles, and permissions'},
        {'name': 'plan:view', 'description': 'View capacity plan'},
        {'name': 'plan:edit', 'description': 'Edit capacity plan'},
        {'name': 'routing:view', 'description': 'View routings'},
        {'name': 'routing:edit', 'description': 'Edit routings'},
    ]
    permissions = [Permission(**p) for p in permissions_data]
    
    # --- 4. Create Organizational Data ---
    # Note: We use the admin_user object for the audit trail
    default_legal_entity = LegalEntity(
        name='Default Legal Entity', 
        created_by_id=admin_user.id, 
        updated_by_id=admin_user.id
    )
    default_bu = BusinessUnit(
        name='Default BU', 
        description='Default Business Unit for initial setup',
        created_by_id=admin_user.id, 
        updated_by_id=admin_user.id
    )
    # FactoryCluster depends on LegalEntity and BusinessUnit
    default_cluster = FactoryCluster(
        name='Default Cluster',
        business_unit=default_bu,
        legal_entity=default_legal_entity,
        created_by_id=admin_user.id,
        updated_by_id=admin_user.id
    )
    # Plant depends on FactoryCluster
    default_plant = Plant(
        name='Default Plant',
        address='123 Main Street',
        factory_cluster=default_cluster,
        created_by_id=admin_user.id,
        updated_by_id=admin_user.id
    )

    # --- 5. Stage all new objects for addition ---
    db.session.add_all([
        admin_role, planner_role, viewer_role,
        *permissions, # The '*' unpacks the list
        default_legal_entity, default_bu, default_cluster, default_plant
    ])
    # Commit here to ensure permissions and roles have IDs before assignment
    db.session.commit()

    # --- 6. Assign Permissions to Roles ---
    perm_map = {p.name: p for p in Permission.query.all()}
    admin_role.permissions.extend([perm_map['admin:all'], perm_map['user:manage']])
    planner_role.permissions.extend([perm_map['plan:view'], perm_map['plan:edit'], perm_map['routing:view']])
    viewer_role.permissions.extend([perm_map['plan:view'], perm_map['routing:view']])

    # --- 7. Assign Roles to Users ---
    admin_user.roles.append(admin_role)
    planner_user.roles.append(planner_role)
    
    # --- 8. Create Menus ---
    menu_dashboard = Menu(name='Dashboard', route='/dashboard', icon='bi-grid', order_num=1)
    menu_planning = Menu(name='Capacity Planning', route='/planning', icon='bi-bar-chart-line', order_num=10, required_permission_id=perm_map['plan:view'].id)
    menu_mfg_data = Menu(name='Manufacturing Data', route='/mfg-data', icon='bi-box-seam', order_num=20)
    menu_routings = Menu(name='Routings', route='/routings', icon='bi-diagram-3', order_num=21, parent=menu_mfg_data, required_permission_id=perm_map['routing:view'].id)
    menu_admin = Menu(name='System Admin', route='/admin', icon='bi-gear', order_num=100, required_permission_id=perm_map['user:manage'].id)
    menu_users = Menu(name='User Management', route='/admin/users', icon='bi-people', order_num=101, parent=menu_admin, required_permission_id=perm_map['user:manage'].id)
    menu_roles = Menu(name='Role Management', route='/admin/roles', icon='bi-person-badge', order_num=102, parent=menu_admin, required_permission_id=perm_map['user:manage'].id)

    db.session.add_all([menu_dashboard, menu_planning, menu_mfg_data, menu_routings, menu_admin, menu_users, menu_roles])
    
    # --- Final Commit ---
    db.session.commit()
    print("Database seeded successfully!")