# goji/app/apis/auth.py
from flask import Blueprint, request, jsonify, current_app
from ..user_management import User, PasswordResetToken
from ..user_management.schemas import UserSchema # Import UserSchema
from ..extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from marshmallow import ValidationError
from datetime import datetime, timedelta
import secrets

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

user_schema = UserSchema() # Instantiate for single user serialization

@bp.route("/login", methods=["POST"])
def login():
    """Authenticates a user and returns a JWT access token."""
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400 # Explicitly handle missing fields

    user = User.query.filter_by(username=username, is_active=True).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        # Return user info along with the token for convenience
        return jsonify({
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name
            }
        })

    return jsonify({"msg": "Bad username or password"}), 401


@bp.route("/register", methods=["POST"])
def register():
    """
    Registers a new user.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400

    try:
        # UserSchema's @post_load handles password hashing and user creation
        new_user = user_schema.load(json_data)
        
        # Check if username or email already exists
        if User.query.filter_by(username=new_user.username).first():
            return jsonify({"msg": "Username already exists"}), 409
        if User.query.filter_by(email=new_user.email).first():
            return jsonify({"msg": "Email already exists"}), 409
        db.session.add(new_user)
        db.session.commit()
        
        # Return the created user's data (excluding sensitive info)
        return jsonify(user_schema.dump(new_user)), 201
        
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        # Catch other potential errors during registration
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
    

@bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Unsets the JWT access token cookie, effectively logging the user out."""
    response = jsonify({"msg": "Successfully logged out"})
    unset_jwt_cookies(response)
    return response


@bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Gets the current user's information."""
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify(user_schema.dump(user)), 200


@bp.route("/admin/password/reset/request", methods=["POST"])
@jwt_required()
def admin_request_password_reset():
    """
    Requests a password reset for a specific user by an administrator.
    Returns the reset link (containing a random token).
    """
    current_user_id = get_jwt_identity()
    admin_user = db.session.get(User, current_user_id)

    if not admin_user:
        return jsonify({"msg": "Admin user not found"}), 404

    # Check if the admin user has the 'admin:all' permission
    admin_permissions = {perm.name for role in admin_user.roles for perm in role.permissions}
    if 'admin:all' not in admin_permissions:
        return jsonify({"msg": "You don't have permission to perform this action"}), 403

    # Get the target user's ID from the request
    target_user_id = request.json.get("user_id", None)
    if not target_user_id:
        return jsonify({"msg": "User ID is required"}), 400

    # Find the target user
    target_user = db.session.get(User, target_user_id)
    if not target_user:
        return jsonify({"msg": "Target user not found"}), 404

    # Generate a unique token
    reset_token = secrets.token_urlsafe(32)
    # Set an expiration date (e.g., 1 hour from now)
    expiration_date = datetime.utcnow() + timedelta(hours=1)

    # Store the token in the database
    reset_token_entry = PasswordResetToken(user=target_user, token=reset_token, expiration_date=expiration_date)
    db.session.add(reset_token_entry)
    db.session.commit()

    # Construct the reset link
    reset_link = f"{current_app.config.get('FRONTEND_URL')}/reset-password?token={reset_token}"

    # Return the reset link (instead of sending an email)
    return jsonify({
        "msg": "Password reset link generated successfully",
        "reset_link": reset_link # Return the reset link
    }), 200

@bp.route("/password/reset/confirm", methods=["POST"])
def confirm_password_reset():
    """Confirms password reset with token and new password."""
    token = request.json.get("token", None)
    new_password = request.json.get("new_password", None)

    if not token or not new_password:
        return jsonify({"msg": "Token and new password are required"}), 400

    # Find the token in the database
    reset_token_entry = PasswordResetToken.query.filter_by(token=token).first()

    if not reset_token_entry:
        return jsonify({"msg": "Invalid reset token"}), 400

    if reset_token_entry.is_expired():
        db.session.delete(reset_token_entry)
        db.session.commit()
        return jsonify({"msg": "Reset token has expired"}), 410 # 410 Gone

    user = reset_token_entry.user
    # Hash the new password
    user.set_password(new_password)

    # Delete the token from the database
    db.session.delete(reset_token_entry)
    db.session.commit()

    return jsonify({"msg": "Password reset successfully"}), 200