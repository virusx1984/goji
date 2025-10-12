# goji/app/apis/auth.py
from flask import Blueprint, request, jsonify
from ..user_management import User
from ..user_management.schemas import UserSchema # Import UserSchema
from ..extensions import db
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError

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