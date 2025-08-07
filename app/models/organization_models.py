# goji/app/models/organization_models.py
from ..extensions import db
from .base_model import ModelBase

# These are placeholder models required by the user_permission_models
# for foreign key relationships. In a real project, they would be fully defined.

class Plant(ModelBase):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    # ... add other fields like address, cluster_id, etc.

class BusinessUnit(ModelBase):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    # ... add other fields like description, etc.
