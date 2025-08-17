# goji/app/apis/users.py
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from ..extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

# --- Change: Import models and now schemas ---
from ..models import User, Role, Permission, Menu
from ..schemas import UserSchema, RoleSchema, PermissionSchema, MenuSchema, RoleSimpleSchema

# --- Change: Align Blueprint name with the filename for consistency ---
bp = Blueprint('users', __name__, url_prefix='/api')

# --- Change: Instantiate all necessary schemas for reuse ---
user_schema = UserSchema()
users_schema = UserSchema(many=True)
role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)
permission_schema = PermissionSchema()
permissions_schema = PermissionSchema(many=True)
menu_schema_single = MenuSchema() # For single menu item serialization
menus_schema = MenuSchema(many=True) # For the final menu tree

# --- Decorator for Permission Checks (No changes here) ---
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

    # 1. Define the permission check logic
    user_permission_ids = {perm.id for role in user.roles for perm in role.permissions}
    is_admin = any('admin:all' in p.name for r in user.roles for p in r.permissions)

    def can_access(menu):
        if is_admin: return True
        return menu.required_permission_id is None or menu.required_permission_id in user_permission_ids
    
    # 2. Fetch only the top-level menus
    top_level_menus = Menu.query.filter(Menu.parent_id.is_(None)).order_by(Menu.order_num).all()

    # 3. Filter the top-level menus first
    accessible_top_level = [menu for menu in top_level_menus if can_access(menu)]

    # 4. Instantiate the schema, passing the check function in the context
    # The schema will now handle the recursion and filtering internally.
    schema_with_context = MenuSchema(many=True, context={'can_access': can_access})

    return jsonify(schema_with_context.dump(accessible_top_level))

# =============================================
# User API Endpoints
# =============================================
@bp.route("/users", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_users():
    """Gets a list of all users."""
    users = User.query.all()
    # --- Change: Use schema to serialize the list of users ---
    return jsonify(users_schema.dump(users))

@bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_user(user_id):
    """Gets a single user by ID."""
    user = User.query.get_or_404(user_id)
    # --- Change: Use schema to serialize a single user ---
    return jsonify(user_schema.dump(user))

@bp.route("/users", methods=["POST"])
@jwt_required()
@permission_required('user:manage')
def create_user():
    """Creates a new user."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400
    
    # --- Change: Use schema to validate and deserialize input ---
    try:
        # The @post_load in the schema handles User instance creation and password hashing
        new_user = user_schema.load(json_data)
        
        # Handle role assignments separately after loading the user instance
        if 'role_ids' in json_data:
            new_user.roles = Role.query.filter(Role.id.in_(json_data['role_ids'])).all()

        db.session.add(new_user)
        db.session.commit()
        return jsonify(user_schema.dump(new_user)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

@bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
@permission_required('user:manage')
def update_user(user_id):
    """Updates a user's information and assigned roles."""
    user = User.query.get_or_404(user_id)
    json_data = request.get_json()
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400

    # --- Change: Use schema to validate and load data into the existing user instance ---
    try:
        # The schema's @post_load will update the user instance with new data
        updated_user = user_schema.load(json_data, instance=user, partial=True)

        # Handle role assignments separately after loading
        if 'role_ids' in json_data:
            updated_user.roles = Role.query.filter(Role.id.in_(json_data['role_ids'])).all()

        db.session.commit()
        return jsonify(user_schema.dump(updated_user))
    except ValidationError as err:
        return jsonify(err.messages), 400

# =============================================
# Role & Permission API Endpoints
# =============================================
@bp.route("/roles", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_roles():
    """Gets a list of all roles."""
    roles = Role.query.all()
    # --- Change: Use schema for serialization ---
    return jsonify(roles_schema.dump(roles))

@bp.route("/roles/<int:role_id>", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_role(role_id):
    """Gets a single role by ID."""
    role = Role.query.get_or_404(role_id)
    # --- Change: Use schema for serialization ---
    return jsonify(role_schema.dump(role))

@bp.route("/roles", methods=["POST"])
@jwt_required()
@permission_required('user:manage')
def create_role():
    """Creates a new role."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400
    # --- Change: Use schema for validation and deserialization ---
    try:
        new_role = role_schema.load(json_data)
        
        # Handle permission assignments after loading
        if 'permission_ids' in json_data:
            new_role.permissions = Permission.query.filter(Permission.id.in_(json_data['permission_ids'])).all()

        db.session.add(new_role)
        db.session.commit()
        return jsonify(role_schema.dump(new_role)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

@bp.route("/roles/<int:role_id>", methods=["PUT"])
@jwt_required()
@permission_required('user:manage')
def update_role(role_id):
    """Updates a role's information and assigned permissions."""
    role = Role.query.get_or_404(role_id)
    json_data = request.get_json()
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400
    # --- Change: Use schema to load data into the existing role instance ---
    try:
        updated_role = role_schema.load(json_data, instance=role, partial=True)

        # Handle permission assignments after loading
        if 'permission_ids' in json_data:
            updated_role.permissions = Permission.query.filter(Permission.id.in_(json_data['permission_ids'])).all()
        
        db.session.commit()
        return jsonify(role_schema.dump(updated_role))
    except ValidationError as err:
        return jsonify(err.messages), 400

@bp.route("/permissions", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_permissions():
    """Gets a list of all available permissions."""
    permissions = Permission.query.all()
    # --- Change: Use schema for serialization ---
    return jsonify(permissions_schema.dump(permissions))
