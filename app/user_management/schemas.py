# goji/app/user_management/schemas.py
from marshmallow import fields, validate, post_load
from ..extensions import ma
from .models import User, Role, Permission, Menu

class PermissionSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the Permission model."""
    class Meta:
        model = Permission
        load_instance = True

class RoleSimpleSchema(ma.SQLAlchemyAutoSchema):
    """A simple Role schema for nested display, excluding permissions."""
    class Meta:
        model = Role

class RoleSchema(ma.SQLAlchemyAutoSchema):
    """A complete schema for Role, including nested permissions."""
    permissions = fields.Nested(PermissionSchema, many=True, dump_only=True)
    # 'permission_ids' is a write-only field for updating the relationship
    permission_ids = fields.List(fields.Int(), load_only=True)

    class Meta:
        model = Role
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
        exclude = ('password_hash',)
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
    # This field will call the 'get_accessible_children' method below.
    children = fields.Method("get_accessible_children")

    class Meta:
        model = Menu
        load_instance = True

    
    def get_accessible_children(self, menu_obj):
        """
        This method is called by the 'children' field. It filters the children
        based on permissions passed in the schema's context.
        """
        # Get the permission check function from the context
        can_access = self.context.get('can_access')
        if not can_access:
            return []

        accessible_children = []
        for child in menu_obj.children:
            if can_access(child):
                accessible_children.append(child)
        
        # Serialize the filtered children using the same schema instance
        return MenuSchema(many=True, context=self.context).dump(accessible_children)