# goji/app/commands.py
from flask.cli import with_appcontext
import click
from .extensions import db
from .models import User, Role, Permission, Menu, Plant, BusinessUnit, user_roles, role_permissions

@click.command(name='seed')
@with_appcontext
def seed_data_command():
    """Seeds the database with initial data."""
    print("Seeding database...")
    
    # Clean up old data in a specific order to respect foreign keys
    db.session.execute(user_roles.delete())
    db.session.execute(role_permissions.delete())
    Menu.query.delete()
    Permission.query.delete()
    Role.query.delete()
    User.query.delete()
    Plant.query.delete()
    BusinessUnit.query.delete()
    db.session.commit()

    # Create base organization data
    default_bu = BusinessUnit(name='Default BU')
    default_plant = Plant(name='Default Plant')
    db.session.add_all([default_bu, default_plant])
    db.session.commit()

    # Create users
    admin_user = User(username='admin', full_name='System Administrator', email='admin@goji.com', is_active=True)
    admin_user.set_password('supersecret')
    
    planner_user = User(username='planner1', full_name='Planner John', email='planner1@goji.com', is_active=True)
    planner_user.set_password('password123')

    db.session.add_all([admin_user, planner_user])
    db.session.commit()

    # Create roles
    admin_role = Role(name='Administrator', description='Has all permissions')
    planner_role = Role(name='Planner', description='Responsible for capacity planning')
    viewer_role = Role(name='Viewer', description='Read-only access')
    
    db.session.add_all([admin_role, planner_role, viewer_role])
    db.session.commit()

    # Create permissions
    permissions_data = [
        {'name': 'admin:all', 'description': 'Super administrator permission'},
        {'name': 'user:manage', 'description': 'Manage users and roles'},
        {'name': 'plan:view', 'description': 'View capacity plan'},
        {'name': 'plan:edit', 'description': 'Edit capacity plan'},
        {'name': 'routing:view', 'description': 'View routings'},
        {'name': 'routing:edit', 'description': 'Edit routings'},
    ]
    permissions = [Permission(**p) for p in permissions_data]
    db.session.add_all(permissions)
    db.session.commit()

    # Assign permissions to roles
    perm_map = {p.name: p for p in Permission.query.all()}
    admin_role.permissions.append(perm_map['admin:all'])
    admin_role.permissions.append(perm_map['user:manage']) # Admin should also have user manage
    
    planner_role.permissions.append(perm_map['plan:view'])
    planner_role.permissions.append(perm_map['plan:edit'])
    planner_role.permissions.append(perm_map['routing:view'])
    
    viewer_role.permissions.append(perm_map['plan:view'])
    viewer_role.permissions.append(perm_map['routing:view'])

    # Assign roles to users
    admin_user.roles.append(admin_role)
    planner_user.roles.append(planner_role)
    
    # Create menus
    menu_dashboard = Menu(name='Dashboard', route='/dashboard', icon='bi-grid', order_num=1)
    menu_planning = Menu(name='Capacity Planning', route='/planning', icon='bi-bar-chart-line', order_num=10, required_permission_id=perm_map['plan:view'].id)
    menu_mfg_data = Menu(name='Manufacturing Data', route='/mfg-data', icon='bi-box-seam', order_num=20)
    menu_routings = Menu(name='Routings', route='/routings', icon='bi-diagram-3', order_num=21, parent=menu_mfg_data, required_permission_id=perm_map['routing:view'].id)
    
    menu_admin = Menu(name='System Admin', route='/admin', icon='bi-gear', order_num=100, required_permission_id=perm_map['user:manage'].id)
    menu_users = Menu(name='User Management', route='/admin/users', icon='bi-people', order_num=101, parent=menu_admin, required_permission_id=perm_map['user:manage'].id)
    menu_roles = Menu(name='Role Management', route='/admin/roles', icon='bi-person-badge', order_num=102, parent=menu_admin, required_permission_id=perm_map['user:manage'].id)

    db.session.add_all([menu_dashboard, menu_planning, menu_mfg_data, menu_routings, menu_admin, menu_users, menu_roles])
    
    db.session.commit()
    print("Database seeded successfully!")
