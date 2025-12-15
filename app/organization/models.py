# goji/app/organization/models.py
from ..extensions import db
from ..models import ModelBase, AuditMixin
from datetime import datetime

class BusinessUnit(ModelBase, AuditMixin):
    """
    Defines the highest-level business units in the company.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(500))




class LegalEntity(ModelBase, AuditMixin):
    """
    Stores information for all independent legal entities.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    tax_id = db.Column(db.String(100), unique=True, index=True)
    address = db.Column(db.String(500))
    legal_rep = db.Column(db.String(100))


class FactoryCluster(ModelBase, AuditMixin):
    """
    Defines a cluster of factories, linked to a BU and a Legal Entity.
    """
    id = db.Column(db.Integer, primary_key=True)
    bu_id = db.Column(db.Integer, db.ForeignKey('gj_business_units.id'), nullable=False)
    legal_entity_id = db.Column(db.Integer, db.ForeignKey('gj_legal_entities.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, unique=True)



class Plant(ModelBase, AuditMixin):
    """
    Defines a specific manufacturing plant or facility.
    """
    id = db.Column(db.Integer, primary_key=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('gj_factory_clusters.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(500))

