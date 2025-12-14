# goji/app/system/routes.py

from flask import Blueprint, jsonify
from .services import system_service
from .schemas import AuditLogSchema
from flask_jwt_extended import jwt_required

# Helper decorators from user_management (assuming they are reusable or duplicated here)
# In a real app, move 'permission_required' to a shared 'goji/utils/decorators.py'
from ..user_management.routes import permission_required 

bp = Blueprint('system', __name__, url_prefix='/api/system')

audit_logs_schema = AuditLogSchema(many=True)

@bp.route('/audit-logs', methods=['GET'])
@jwt_required()
@permission_required('admin:all') # Strict permission: only super admin can view logs
def get_audit_logs():
    """Get all system audit logs."""
    logs = system_service.get_all_audit_logs()
    return jsonify(audit_logs_schema.dump(logs))

@bp.route('/audit-logs/user/<int:user_id>', methods=['GET'])
@jwt_required()
@permission_required('admin:all')
def get_user_audit_logs(user_id):
    """Get audit logs for a specific user."""
    logs = system_service.get_audit_logs_by_user(user_id)
    return jsonify(audit_logs_schema.dump(logs))