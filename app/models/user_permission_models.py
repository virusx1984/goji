# goji/app/models/user_permission_models.py
from ..extensions import db, bcrypt
from datetime import datetime

# --- Association Tables ---

user_roles = db.Table('user_roles',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), nullable=False),
    db.Column('plant_id', db.Integer, db.ForeignKey('plants.id'), nullable=True),
    db.Column('bu_id', db.Integer, db.ForeignKey('business_units.id'), nullable=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False),
    db.Column('created_by_id', db.Integer, db.ForeignKey('users.id')),
    db.UniqueConstraint('user_id', 'role_id', 'plant_id', 'bu_id', name='uq_user_role_scope')
)

role_permissions = db.Table('role_permissions',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), nullable=False),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), nullable=False),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False),
    db.Column('created_by_id', db.Integer, db.ForeignKey('users.id')),
    db.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission')
)

# --- Main Models ---

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "is_active": self.is_active,
            "roles": [role.to_dict_simple() for role in self.roles]
        }

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    permissions = db.relationship('Permission', secondary=role_permissions, backref=db.backref('roles', lazy='dynamic'))
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "permissions": [p.to_dict() for p in self.permissions]
        }
        
    def to_dict_simple(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False) # e.g., 'user:create'
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

class Menu(db.Model):
    __tablename__ = 'menus'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    route = db.Column(db.String(255))
    icon = db.Column(db.String(100))
    order_num = db.Column(db.Integer, default=0)
    required_permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=True)

    required_permission = db.relationship('Permission')
    children = db.relationship('Menu', backref=db.backref('parent', remote_side=[id]), lazy='dynamic', order_by='Menu.order_num')
    
    def to_dict(self):
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "name": self.name,
            "route": self.route,
            "icon": self.icon,
            "order_num": self.order_num,
            "children": [child.to_dict() for child in self.children]
        }
