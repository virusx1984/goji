# goji/app/apis/auth_api.py
from flask import Blueprint, request, jsonify
from ..models import User
from flask_jwt_extended import create_access_token

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route("/login", methods=["POST"])
def login():
    """
    Authenticates a user and returns a JWT access token.
    """
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    
    user = User.query.filter_by(username=username, is_active=True).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token)

    return jsonify({"msg": "Bad username or password"}), 401
