# goji/app/models/user_permission_models.py
from ..extensions import db, bcrypt
from datetime import datetime
from .base_model import ModelBase

# --- Association Tables ---

user_roles = db.Table('gj_user_roles',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('gj_users.id'), nullable=False),
    db.Column('role_id', db.Integer, db.ForeignKey('gj_roles.id'), nullable=False),
    db.Column('plant_id', db.Integer, db.ForeignKey('gj_plants.id'), nullable=True),
    db.Column('bu_id', db.Integer, db.ForeignKey('gj_business_units.id'), nullable=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False),
    db.Column('created_by_id', db.Integer, db.ForeignKey('gj_users.id')),
    db.UniqueConstraint('user_id', 'role_id', 'plant_id', 'bu_id', name='uq_user_role_scope')
)

role_permissions = db.Table('gj_role_permissions',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('gj_roles.id'), nullable=False),
    db.Column('permission_id', db.Integer, db.ForeignKey('gj_permissions.id'), nullable=False),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False),
    db.Column('created_by_id', db.Integer, db.ForeignKey('gj_users.id')),
    db.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission')
)

# --- Main Models ---

class User(ModelBase):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    roles = db.relationship(
        'Role',
        secondary=user_roles,
        primaryjoin=(id == user_roles.c.user_id),
        backref=db.backref('users', lazy='dynamic')
    )

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # Removed to_dict() method, now handled by UserSchema

class Role(ModelBase):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    permissions = db.relationship('Permission', secondary=role_permissions, backref=db.backref('roles', lazy='dynamic'))
    
    # Removed to_dict() and to_dict_simple(), now handled by RoleSchema and RoleSimpleSchema

class Permission(ModelBase):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Removed to_dict() method, now handled by PermissionSchema

class Menu(ModelBase):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('gj_menus.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    route = db.Column(db.String(255))
    icon = db.Column(db.String(100))
    order_num = db.Column(db.Integer, default=0)
    required_permission_id = db.Column(db.Integer, db.ForeignKey('gj_permissions.id'), nullable=True)

    required_permission = db.relationship('Permission')
    children = db.relationship('Menu', backref=db.backref('parent', remote_side=[id]), lazy='dynamic', order_by='Menu.order_num')
    
    # Removed to_dict() method, now handled by MenuSchema

