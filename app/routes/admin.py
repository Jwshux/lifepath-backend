from flask import Blueprint, current_app, jsonify, request

from ..extensions import db
from ..models.feedback import (
    delete_feedback,
    get_all_feedback,
)
from ..models.release import (
    get_current_release,
    replace_current_release,
)
from ..utils.admin import admin_required
from ..utils.storage import (
    build_release_object_key,
    calculate_file_metadata,
    delete_object,
    upload_apk,
    validate_apk_file,
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

    current_release = get_current_release()

    current_version = None
    latest_upload = None

    if current_release:
        current_version = current_release.get('version')
        latest_upload = current_release.get('uploaded_at')

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


@admin_bp.get('/releases')
@admin_required
def get_admin_release(current_admin):
    release = get_current_release()

    return jsonify({
        'release': release,
    }), 200


@admin_bp.post('/releases')
@admin_required
def upload_release(current_admin):
    version = (
        request.form.get('version') or ''
    ).strip()

    android_requirement = (
        request.form.get('android_requirement') or ''
    ).strip()

    release_notes = (
        request.form.get('release_notes') or ''
    ).strip()

    uploaded_file = request.files.get('apk')

    if not version:
        return jsonify({
            'error': 'Version is required.',
        }), 400

    if len(version) > 50:
        return jsonify({
            'error': 'Version must not exceed 50 characters.',
        }), 400

    if not android_requirement:
        return jsonify({
            'error': 'Android requirement is required.',
        }), 400

    if len(android_requirement) > 100:
        return jsonify({
            'error': (
                'Android requirement must not exceed '
                '100 characters.'
            ),
        }), 400

    if len(release_notes) > 5000:
        return jsonify({
            'error': (
                'Release notes must not exceed '
                '5,000 characters.'
            ),
        }), 400

    try:
        file_name = validate_apk_file(uploaded_file)

        file_size, sha256 = calculate_file_metadata(
            uploaded_file
        )

        object_key = build_release_object_key(
            file_name
        )

        upload_apk(
            uploaded_file,
            object_key,
        )
    except ValueError as error:
        return jsonify({
            'error': str(error),
        }), 400
    except Exception:
        current_app.logger.exception(
            'Failed to upload APK to Cloudflare R2.'
        )

        return jsonify({
            'error': 'Unable to upload the APK.',
        }), 500

    try:
        release, previous_release = replace_current_release(
            version=version,
            android_requirement=android_requirement,
            release_notes=release_notes,
            file_name=file_name,
            file_size=file_size,
            object_key=object_key,
            sha256=sha256,
            uploaded_by=current_admin['_id'],
        )
    except Exception:
        current_app.logger.exception(
            'Failed to save release metadata.'
        )

        try:
            delete_object(object_key)
        except Exception:
            current_app.logger.exception(
                'Failed to clean up the new R2 object.'
            )

        return jsonify({
            'error': 'Unable to save the release.',
        }), 500

    previous_object_key = (
        previous_release.get('object_key')
        if previous_release
        else None
    )

    if (
        previous_object_key
        and previous_object_key != object_key
    ):
        try:
            delete_object(previous_object_key)
        except Exception:
            current_app.logger.exception(
                'Release updated, but the previous R2 '
                'object could not be deleted.'
            )

    return jsonify({
        'message': 'Game release uploaded successfully.',
        'release': release,
    }), 201