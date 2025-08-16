# goji/app/schemas/user_management_schemas.py
from marshmallow import fields, validate, post_load
from ..extensions import ma
from ..models import User, Role, Permission, Menu

class PermissionSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Permission model."""
    class Meta:
        model = Permission
        fields = ("id", "name", "description")
        load_instance = True

class RoleSimpleSchema(ma.SQLAlchemyAutoSchema):
    """A simple Role schema for nested display, excluding permissions."""
    class Meta:
        model = Role
        fields = ("id", "name")

class RoleSchema(ma.SQLAlchemyAutoSchema):
    """A complete schema for Role, including nested permissions."""
    permissions = fields.Nested(PermissionSchema, many=True, dump_only=True)
    # 'permission_ids' is a write-only field for updating the relationship
    permission_ids = fields.List(fields.Int(), load_only=True)

    class Meta:
        model = Role
        fields = ("id", "name", "description", "permissions", "permission_ids")
        load_instance = True

class UserSchema(ma.SQLAlchemyAutoSchema):
    """Schema for User, handling password securely and role assignments."""
    roles = fields.Nested(RoleSimpleSchema, many=True, dump_only=True)
    # 'password' is write-only for security and has validation
    password = fields.Str(required=False, load_only=True, validate=validate.Length(min=6))
    # 'role_ids' is a write-only field for updating the relationship
    role_ids = fields.List(fields.Int(), load_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "full_name", "email", "is_active", "roles", "password", "role_ids")
        load_instance = False # We handle instance creation manually with @post_load

    @post_load
    def make_user(self, data, **kwargs):
        """
        Custom logic to handle password hashing after data is loaded and validated.
        """
        password = data.pop('password', None)
        # 'role_ids' is not a direct model field, so remove it before creating the instance
        if 'role_ids' in data:
            del data['role_ids']
        
        user = User(**data)
        if password:
            user.set_password(password)
        return user

class MenuSchema(ma.SQLAlchemyAutoSchema):
    """Schema for Menu, handling recursive children for tree structures."""
    required_permission = ma.Nested(PermissionSchema, dump_only=True)
    # Use 'self' for recursive nesting
    children = fields.Nested('self', many=True, dump_only=True) 

    class Meta:
        model = Menu
        # --- REMOVE THE 'fields' TUPLE ---
        # By removing 'fields', SQLAlchemyAutoSchema will automatically include
        # all columns from the Menu model, which is the desired behavior.
        load_instance = True # It's good practice to add this
