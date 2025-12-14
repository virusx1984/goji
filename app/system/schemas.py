# goji/app/system/schemas.py

from ..extensions import ma
from .models import AuditLog

class AuditLogSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema for serializing Audit Logs.
    """
    class Meta:
        model = AuditLog
        load_instance = True
        include_fk = True # Include foreign keys (user_id) in output