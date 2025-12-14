# goji/app/apis/auth.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, unset_jwt_cookies
from marshmallow import ValidationError

# --- Service Layer Import ---
from .services import auth_service
from ..user_management.models import User
from ..user_management.schemas import UserSchema

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Schema for serialization only
user_schema = UserSchema()

@bp.route("/login", methods=["POST"])
def login():
    """Authenticates a user and returns a JWT access token."""
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    result = auth_service.authenticate_user(username, password)
    
    if result:
        return jsonify({
            "access_token": result["access_token"],
            "user": {
                "id": result["user"].id,
                "username": result["user"].username,
                "full_name": result["user"].full_name
            }
        })

    return jsonify({"msg": "Bad username or password"}), 401

@bp.route("/register", methods=["POST"])
def register():
    """Registers a new user."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400

    try:
        new_user = auth_service.register_user(json_data)
        return jsonify(user_schema.dump(new_user)), 201
    except ValueError as e:
        return jsonify({"msg": str(e)}), 409
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500

@bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Unsets the JWT access token cookie."""
    response = jsonify({"msg": "Successfully logged out"})
    unset_jwt_cookies(response)
    return response

@bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Gets the current user's information."""
    current_user_id = get_jwt_identity()
    # Direct query here is acceptable as it's a simple retrieval
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify(user_schema.dump(user)), 200

@bp.route("/admin/password/reset/request", methods=["POST"])
@jwt_required()
def admin_request_password_reset():
    """
    Requests a password reset link (Admin only).
    """
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(current_user_id)

    # Permission Check (Controller Level Logic)
    # Check if admin has 'admin:all' permission
    admin_permissions = {perm.name for role in admin_user.roles for perm in role.permissions}
    if 'admin:all' not in admin_permissions:
        return jsonify({"msg": "You don't have permission to perform this action"}), 403

    target_user_id = request.json.get("user_id")
    if not target_user_id:
        return jsonify({"msg": "User ID is required"}), 400

    try:
        frontend_url = current_app.config.get('FRONTEND_URL')
        reset_link = auth_service.generate_password_reset_token(
            current_user_id, target_user_id, frontend_url
        )
        return jsonify({
            "msg": "Password reset link generated successfully",
            "reset_link": reset_link
        }), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 404

@bp.route("/password/reset/confirm", methods=["POST"])
def confirm_password_reset():
    """Confirms password reset with token."""
    token = request.json.get("token")
    new_password = request.json.get("new_password")

    if not token or not new_password:
        return jsonify({"msg": "Token and new password are required"}), 400

    try:
        auth_service.confirm_password_reset(token, new_password)
        return jsonify({"msg": "Password reset successfully"}), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except TimeoutError as e:
        return jsonify({"msg": str(e)}), 410 # 410 Gone