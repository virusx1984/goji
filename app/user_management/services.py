# goji/app/user_management/services.py

from ..extensions import db
from .models import User, Role, Permission, Menu
from .schemas import UserSchema, RoleSchema
from marshmallow import ValidationError

# =========================================================
# User Service (Existing)
# =========================================================
class UserService:
    """
    Encapsulates all business logic related to user management.
    """

    def __init__(self):
        self.user_schema = UserSchema()
        self.user_schema_partial = UserSchema(partial=True) 

    def get_all_users(self):
        """Retrieves all users."""
        return User.query.all()

    def get_user_by_id(self, user_id):
        """Retrieves a single user or raises 404."""
        return User.query.get_or_404(user_id)

    def create_user(self, data: dict) -> User:
        """Handles full user creation process."""
        try:
            role_ids = data.get('role_ids', [])
            new_user = self.user_schema.load(data)
            
            if role_ids:
                roles = Role.query.filter(Role.id.in_(role_ids)).all()
                new_user.roles = roles

            db.session.add(new_user)
            db.session.commit()
            return new_user
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    def update_user(self, user_id: int, data: dict) -> User:
        """Handles user updates."""
        user = self.get_user_by_id(user_id)
        try:
            role_ids = data.get('role_ids')
            updated_user = self.user_schema_partial.load(data, instance=user)

            if role_ids is not None:
                updated_user.roles = Role.query.filter(Role.id.in_(role_ids)).all()

            db.session.commit()
            return updated_user
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    def delete_user(self, user_id: int):
        """Deletes a user."""
        user = self.get_user_by_id(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


# =========================================================
# Role Service (New)
# =========================================================
class RoleService:
    """
    Encapsulates business logic for Roles and Permissions.
    """
    def __init__(self):
        self.role_schema = RoleSchema()
        self.role_schema_partial = RoleSchema(partial=True)

    def get_all_roles(self):
        """Retrieves all roles."""
        return Role.query.all()

    def get_role_by_id(self, role_id):
        """Retrieves a single role or raises 404."""
        return Role.query.get_or_404(role_id)

    def create_role(self, data: dict) -> Role:
        """Creates a new role and assigns permissions."""
        try:
            # Extract permission_ids before loading schema
            permission_ids = data.get('permission_ids', [])
            
            new_role = self.role_schema.load(data)

            # Handle Permission Association
            if permission_ids:
                permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
                new_role.permissions = permissions

            db.session.add(new_role)
            db.session.commit()
            return new_role
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    def update_role(self, role_id: int, data: dict) -> Role:
        """Updates an existing role."""
        role = self.get_role_by_id(role_id)
        try:
            permission_ids = data.get('permission_ids') # None = no change, [] = clear all

            updated_role = self.role_schema_partial.load(data, instance=role)

            if permission_ids is not None:
                permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
                updated_role.permissions = permissions

            db.session.commit()
            return updated_role
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    def get_all_permissions(self):
        """Retrieves all available system permissions."""
        return Permission.query.all()


# =========================================================
# Menu Service (New)
# =========================================================
class MenuService:
    """
    Encapsulates logic for menu retrieval and permission filtering.
    """

    @staticmethod
    def can_access(menu, is_admin, user_permission_ids):
        """
        Static logic to determine if a menu item is accessible.
        Used by the Schema context during serialization.
        """
        if is_admin:
            return True
        return menu.required_permission_id is None or menu.required_permission_id in user_permission_ids

    def get_menu_tree_context(self, user_id):
        """
        Prepares the menu data and the permission context for a specific user.
        
        Returns:
            tuple: (top_level_menus, context_dictionary)
        """
        user = User.query.get(user_id)
        if not user:
            return None, None

        # 1. Calculate Permissions
        user_permission_ids = {perm.id for role in user.roles for perm in role.permissions}
        is_admin = any('admin:all' in p.name for r in user.roles for p in r.permissions)

        # 2. Fetch Top-Level Menus
        # We only fetch top-level; children are loaded recursively via relationships in Schema
        top_level_menus = Menu.query.filter(Menu.parent_id.is_(None)).order_by(Menu.order_num).all()

        # 3. Pre-filter Top-Level Menus (Optimization)
        # We filter the roots here, and let the Schema handle the children recursion
        accessible_roots = [
            m for m in top_level_menus 
            if self.can_access(m, is_admin, user_permission_ids)
        ]

        # 4. Prepare Context for Schema
        # The schema needs a callable 'can_access' that binds the current user's state
        context = {
            'can_access': lambda m: self.can_access(m, is_admin, user_permission_ids)
        }

        return accessible_roots, context


# Instantiate services for singleton usage
user_service = UserService()
role_service = RoleService()
menu_service = MenuService()