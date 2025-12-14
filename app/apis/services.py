# goji/app/apis/services.py

from ..extensions import db
from ..user_management.models import User, PasswordResetToken
from ..user_management.schemas import UserSchema
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta
import secrets

class AuthService:
    """
    Encapsulates Authentication logic (Login, Registration, Password Reset).
    """

    def __init__(self):
        self.user_schema = UserSchema()

    def authenticate_user(self, username, password):
        """
        Validates credentials and generates a JWT token.
        Returns:
            dict: { "access_token": str, "user": User } or None
        """
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user and user.check_password(password):
            # Generate JWT Token
            access_token = create_access_token(identity=str(user.id))
            return {
                "access_token": access_token,
                "user": user
            }
        return None

    def register_user(self, data: dict) -> User:
        """
        Registers a new user. 
        Note: Checks for existing username/email should ideally happen here 
        or be handled by database unique constraints.
        """
        # Check for duplicates manually to provide clear error messages
        if User.query.filter_by(username=data.get('username')).first():
            raise ValueError("Username already exists")
        if User.query.filter_by(email=data.get('email')).first():
            raise ValueError("Email already exists")

        # UserSchema.make_user (@post_load) handles password hashing
        new_user = self.user_schema.load(data)
        
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def generate_password_reset_token(self, admin_user_id, target_user_id, frontend_url):
        """
        Generates a secure password reset link.
        """
        # Security Check: Ensure Admin has permission (Logic simplified for Service)
        admin_user = User.query.get(admin_user_id)
        # Note: In a strict service layer, permission checks usually happen before calling this,
        # or we inject a PermissionService. For now, we assume the caller checked permissions.

        target_user = User.query.get(target_user_id)
        if not target_user:
            raise ValueError("Target user not found")

        # Generate Token
        reset_token = secrets.token_urlsafe(32)
        expiration_date = datetime.utcnow() + timedelta(hours=1)

        token_entry = PasswordResetToken(
            user=target_user, 
            token=reset_token, 
            expiration_date=expiration_date
        )
        db.session.add(token_entry)
        db.session.commit()

        return f"{frontend_url}/reset-password?token={reset_token}"

    def confirm_password_reset(self, token, new_password):
        """
        Resets password using a valid token.
        """
        reset_token_entry = PasswordResetToken.query.filter_by(token=token).first()

        if not reset_token_entry:
            raise ValueError("Invalid reset token")

        if reset_token_entry.is_expired():
            db.session.delete(reset_token_entry)
            db.session.commit()
            raise TimeoutError("Reset token has expired")

        user = reset_token_entry.user
        user.set_password(new_password)

        # Invalidate token after use
        db.session.delete(reset_token_entry)
        db.session.commit()

# Singleton instance
auth_service = AuthService()