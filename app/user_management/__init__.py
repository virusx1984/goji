# goji/app/user_management/__init__.py

# This file defines the 'user_management' feature module as a Python package.
# It also exposes the module's key components, like the Blueprint and primary models,
# to make them easily importable from other parts of the application.

from .routes import bp
from .models import User, Role, Permission, Menu, user_roles, role_permissions
from .schemas import UserSchema, RoleSchema, RoleSimpleSchema, PermissionSchema, MenuSchema
