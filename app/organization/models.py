# goji/app/models/organization_models.py
from ..extensions import db
from ..models import ModelBase
from datetime import datetime

class BusinessUnit(ModelBase):
    """
    Defines the highest-level business units in the company.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(500))

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

    # Relationships
    clusters = db.relationship('FactoryCluster', backref='business_unit', lazy='dynamic')

class LegalEntity(ModelBase):
    """
    Stores information for all independent legal entities.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    tax_id = db.Column(db.String(100), unique=True, index=True)
    address = db.Column(db.String(500))
    legal_rep = db.Column(db.String(100))

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

class FactoryCluster(ModelBase):
    """
    Defines a cluster of factories, linked to a BU and a Legal Entity.
    """
    id = db.Column(db.Integer, primary_key=True)
    bu_id = db.Column(db.Integer, db.ForeignKey('gj_business_units.id'), nullable=False)
    legal_entity_id = db.Column(db.Integer, db.ForeignKey('gj_legal_entities.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

    # Relationships
    plants = db.relationship('Plant', backref='factory_cluster', lazy='dynamic')
    legal_entity = db.relationship('LegalEntity')

class Plant(ModelBase):
    """
    Defines a specific manufacturing plant or facility.
    """
    id = db.Column(db.Integer, primary_key=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('gj_factory_clusters.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(500))

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
