# goji/app/user_management/routes.py

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

# --- Service Layer Imports ---
from .services import user_service, role_service, menu_service

# --- Model & Schema Imports ---
from .models import User
from .schemas import (
    UserSchema, 
    RoleSchema, 
    PermissionSchema, 
    MenuSchema
)

bp = Blueprint('users', __name__, url_prefix='/api')

# --- Instantiate Schemas for Serialization (Dump Only) ---
user_schema = UserSchema()
users_schema = UserSchema(many=True)
role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)
permissions_schema = PermissionSchema(many=True)

# =============================================
# Helper Decorators
# =============================================

def permission_required(permission_name):
    """
    Custom decorator to check permissions.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            # We query User directly here for efficiency in the decorator
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
# User Endpoints
# =============================================

@bp.route("/users", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_users():
    users = user_service.get_all_users()
    return jsonify(users_schema.dump(users))

@bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_user(user_id):
    user = user_service.get_user_by_id(user_id)
    return jsonify(user_schema.dump(user))

@bp.route("/users", methods=["POST"])
@jwt_required()
@permission_required('user:manage')
def create_user():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400
    try:
        new_user = user_service.create_user(json_data)
        return jsonify(user_schema.dump(new_user)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
@permission_required('user:manage')
def update_user(user_id):
    json_data = request.get_json()
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400
    try:
        updated_user = user_service.update_user(user_id, json_data)
        return jsonify(user_schema.dump(updated_user)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
@permission_required('user:manage')
def delete_user(user_id):
    try:
        user_service.delete_user(user_id)
        return '', 204
    except Exception as e:
        return jsonify({"msg": str(e)}), 500


# =============================================
# Role Endpoints
# =============================================

@bp.route("/roles", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_roles():
    roles = role_service.get_all_roles()
    return jsonify(roles_schema.dump(roles))

@bp.route("/roles/<int:role_id>", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_role(role_id):
    role = role_service.get_role_by_id(role_id)
    return jsonify(role_schema.dump(role))

@bp.route("/roles", methods=["POST"])
@jwt_required()
@permission_required('user:manage')
def create_role():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400
    try:
        new_role = role_service.create_role(json_data)
        return jsonify(role_schema.dump(new_role)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@bp.route("/roles/<int:role_id>", methods=["PUT"])
@jwt_required()
@permission_required('user:manage')
def update_role(role_id):
    json_data = request.get_json()
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400
    try:
        updated_role = role_service.update_role(role_id, json_data)
        return jsonify(role_schema.dump(updated_role)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@bp.route("/permissions", methods=["GET"])
@jwt_required()
@permission_required('user:manage')
def get_permissions():
    permissions = role_service.get_all_permissions()
    return jsonify(permissions_schema.dump(permissions))


# =============================================
# Menu Endpoints
# =============================================

@bp.route("/menus", methods=["GET"])
@jwt_required()
def get_menus():
    """Get the menu tree accessible to the current user."""
    current_user_id = get_jwt_identity()
    
    # Delegate logic to Service
    menus, context = menu_service.get_menu_tree_context(current_user_id)
    
    if menus is None:
        return jsonify({"msg": "User not found"}), 404

    # Inject context into Schema for recursive filtering
    schema = MenuSchema(many=True, context=context)
    
    return jsonify(schema.dump(menus))