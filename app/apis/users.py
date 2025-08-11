# goji/app/apis/users.py
from flask import Blueprint, jsonify, request
from ..models import User, Role, Permission, Menu
from ..extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

# --- Recommended Change: Align Blueprint name with the filename for consistency ---
bp = Blueprint('users', __name__, url_prefix='/api')

# --- Decorator for Permission Checks ---
def permission_required(permission_name):
    """Custom decorator to check if a user has a specific permission."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user:
                return jsonify({"msg": "User not found"}), 404
            
            user_permissions = {perm.name for role in user.roles for perm in role.permissions}
            
            if 'admin:all' in user_permissions or permission_name in user_permissions:
                return fn(*args, **kwargs)
            else:
                return jsonify({"msg": "Forbidden: You don't have the required permission"}), 403
        return wrapper
    return decorator

# =============================================
# Menu API Endpoints
# =============================================
@bp.route("/menus", methods=["GET"])
@jwt_required()
def get_menus():
    """Gets the accessible menu tree for the current logged-in user."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404

    user_permission_ids = {perm.id for role in user.roles for perm in role.permissions}
    # Admin with 'admin:all' permission should see all menus
    is_admin = any('admin:all' in p.name for r in user.roles for p in r.permissions)

    def can_access(menu):
        if is_admin:
            return True
        return menu.required_permission_id is None or menu.required_permission_id in user_permission_ids

    def build_menu_tree(menu_item):
        if not can_access(menu_item):
            return None
        
        menu_dict = menu_item.to_dict()
        accessible_children = []
        for child in menu_item.children:
            child_tree = build_menu_tree(child)
            if child_tree:
                accessible_children.append(child_tree)
        
        menu_dict['children'] = accessible_children
        return menu_dict

    top_level_menus = Menu.query.filter(Menu.parent_id.is_(None)).order_by(Menu.order_num).all()
    accessible_menu_tree = [menu for menu in [build_menu_tree(m) for m in top_level_menus] if menu is not None]

    return jsonify(accessible_menu_tree)

# =============================================
# User API Endpoints
# =============================================
@bp.route("/users", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_users():
    """Gets a list of all users."""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_user(user_id):
    """Gets a single user by ID."""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

# ... (The rest of the file remains unchanged) ...
@bp.route("/users", methods=["POST"])
@jwt_required()
@permission_required('user:manage')
def create_user():
    """Creates a new user."""
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"msg": "Missing username or password"}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"msg": "Username already exists"}), 409

    new_user = User(
        username=data['username'],
        full_name=data.get('full_name'),
        email=data.get('email')
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

@bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
@permission_required('user:manage')
def update_user(user_id):
    """Updates a user's information and assigned roles."""
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    # Update basic info
    user.full_name = data.get('full_name', user.full_name)
    user.email = data.get('email', user.email)
    user.is_active = data.get('is_active', user.is_active)

    # Update roles
    if 'role_ids' in data:
        user.roles = Role.query.filter(Role.id.in_(data['role_ids'])).all()

    db.session.commit()
    return jsonify(user.to_dict())

# =============================================
# Role & Permission API Endpoints
# =============================================
@bp.route("/roles", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_roles():
    """Gets a list of all roles."""
    roles = Role.query.all()
    return jsonify([role.to_dict() for role in roles])

@bp.route("/roles/<int:role_id>", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_role(role_id):
    """Gets a single role by ID."""
    role = Role.query.get_or_404(role_id)
    return jsonify(role.to_dict())

@bp.route("/roles", methods=["POST"])
@jwt_required()
@permission_required('user:manage')
def create_role():
    """Creates a new role."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"msg": "Missing role name"}), 400

    if Role.query.filter_by(name=data['name']).first():
        return jsonify({"msg": "Role name already exists"}), 409

    new_role = Role(name=data['name'], description=data.get('description'))
    db.session.add(new_role)
    db.session.commit()
    return jsonify(new_role.to_dict()), 201

@bp.route("/roles/<int:role_id>", methods=["PUT"])
@jwt_required()
@permission_required('user:manage')
def update_role(role_id):
    """Updates a role's information and assigned permissions."""
    role = Role.query.get_or_404(role_id)
    data = request.get_json()

    role.name = data.get('name', role.name)
    role.description = data.get('description', role.description)

    if 'permission_ids' in data:
        role.permissions = Permission.query.filter(Permission.id.in_(data['permission_ids'])).all()

    db.session.commit()
    return jsonify(role.to_dict())

@bp.route("/permissions", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_permissions():
    """Gets a list of all available permissions."""
    permissions = Permission.query.all()
    return jsonify([p.to_dict() for p in permissions])
