# goji/app/system/models.py
from ..extensions import db
from ..models import ModelBase
from sqlalchemy.dialects.postgresql import JSONB

class AuditLog(ModelBase):
    """Stores a log of all significant create, update, delete actions."""
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    action_type = db.Column(db.String(50), nullable=False) # e.g., 'CREATE', 'UPDATE', 'DELETE'
    table_name = db.Column(db.String(100))
    record_id = db.Column(db.Integer)
    before_value = db.Column(JSONB)
    after_value = db.Column(JSONB)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User')
