from flask import Blueprint, jsonify

from ..utils.admin import admin_required


admin_bp = Blueprint('admin', __name__)


@admin_bp.get('/me')
@admin_required
def get_admin_profile(current_admin):
    return jsonify({
        'message': 'Admin access granted.',
        'admin': {
            'id': str(current_admin['_id']),
            'username': current_admin['username'],
            'email': current_admin['email'],
            'role': current_admin.get('role', 'user'),
        },
    }), 200