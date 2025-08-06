# goji/app/apis/user_management_api.py
from flask import Blueprint, jsonify, request
from ..models import User, Role, Permission, Menu
from ..extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('user_management', __name__, url_prefix='/api')

@bp.route("/menus", methods=["GET"])
@jwt_required()
def get_menus():
    """
    Gets the accessible menu tree for the current logged-in user.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404

    user_permission_ids = {perm.id for role in user.roles for perm in role.permissions}

    def can_access(menu):
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


@bp.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    """Gets a list of all users."""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@bp.route("/users", methods=["POST"])
@jwt_required()
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

@bp.route("/roles", methods=["GET"])
@jwt_required()
def get_roles():
    """Gets a list of all roles."""
    roles = Role.query.all()
    return jsonify([role.to_dict() for role in roles])

@bp.route("/permissions", methods=["GET"])
@jwt_required()
def get_permissions():
    """Gets a list of all available permissions."""
    permissions = Permission.query.all()
    return jsonify([p.to_dict() for p in permissions])
