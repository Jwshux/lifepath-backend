from flask import Blueprint, jsonify

from ..extensions import db
from ..utils.admin import admin_required
from ..models.feedback import (
    get_all_feedback,
    delete_feedback,
)

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


@admin_bp.get('/dashboard')
@admin_required
def get_dashboard(current_admin):
    registered_users = db.users.count_documents({})
    feedback_received = db.feedback.count_documents({})

    latest_release = db.releases.find_one(
        sort=[('uploaded_at', -1)]
    )

    current_version = None
    latest_upload = None

    if latest_release:
        current_version = latest_release.get('version')

        uploaded_at = latest_release.get('uploaded_at')

        if uploaded_at:
            latest_upload = uploaded_at.isoformat()

    return jsonify({
        'registered_users': registered_users,
        'feedback_received': feedback_received,
        'current_version': current_version,
        'latest_upload': latest_upload,
    }), 200

@admin_bp.get('/feedback')
@admin_required
def get_admin_feedback(current_admin):
    entries = get_all_feedback()

    return jsonify({
        'feedback': entries,
    }), 200

@admin_bp.delete('/feedback/<feedback_id>')
@admin_required
def remove_admin_feedback(feedback_id, current_admin):
    deleted = delete_feedback(feedback_id)

    if not deleted:
        return jsonify({
            'error': 'Feedback not found.',
        }), 404

    return jsonify({
        'message': 'Feedback deleted successfully.',
        'id': feedback_id,
    }), 200