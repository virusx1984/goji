# goji/app/system/services.py

from ..extensions import db
from .models import AuditLog
from .schemas import AuditLogSchema
from marshmallow import ValidationError
from datetime import datetime

class SystemService:
    """
    Encapsulates logic for System-wide features like Audit Logging.
    """

    def __init__(self):
        self.audit_log_schema = AuditLogSchema()

    def get_all_audit_logs(self):
        """Retrieves all audit logs, ordered by timestamp desc."""
        return AuditLog.query.order_by(AuditLog.timestamp.desc()).all()

    def get_audit_logs_by_user(self, user_id):
        """Retrieves audit logs for a specific user."""
        return AuditLog.query.filter_by(user_id=user_id).order_by(AuditLog.timestamp.desc()).all()

    def log_action(self, user_id, action_type, table_name, record_id, before_val=None, after_val=None):
        """
        Records a system action. 
        This method is intended to be called by other Services, not via API.
        """
        try:
            log_entry = AuditLog(
                user_id=user_id,
                action_type=action_type,
                table_name=table_name,
                record_id=record_id,
                before_value=str(before_val) if before_val else None,
                after_value=str(after_val) if after_val else None,
                timestamp=datetime.utcnow()
            )
            db.session.add(log_entry)
            db.session.commit()
            return log_entry
        except Exception as e:
            # Audit logging failure should not crash the main application
            print(f"Failed to create audit log: {e}")
            db.session.rollback()
            return None

# Singleton instance
system_service = SystemService()