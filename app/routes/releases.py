from flask import Blueprint, current_app, jsonify

from ..models.release import get_current_release
from ..utils.storage import generate_download_url
from ..utils.auth import user_required

releases_bp = Blueprint('releases', __name__)


def public_release_data(release):
    if not release:
        return None

    return {
        'version': release.get('version'),
        'android_requirement': release.get(
            'android_requirement'
        ),
        'file_name': release.get('file_name'),
        'file_size': release.get('file_size'),
        'uploaded_at': release.get('uploaded_at'),
    }


@releases_bp.get('/latest')
def get_latest_release():
    release = get_current_release()

    return jsonify({
        'release': public_release_data(release),
    }), 200


@releases_bp.get('/download')
@user_required
def download_latest_release(current_user):
    release = get_current_release()

    if not release:
        return jsonify({
            'error': 'No game release is currently available.',
        }), 404

    try:
        download_url = generate_download_url(
            object_key=release['object_key'],
            download_name=release.get(
                'file_name',
                'LifePATH.apk',
            ),
            expires_in=120,
        )
    except Exception:
        current_app.logger.exception(
            'Failed to generate the APK download URL.'
        )

        return jsonify({
            'error': 'Unable to prepare the download.',
        }), 500

    return jsonify({
        'download_url': download_url,
        'expires_in': 120,
    }), 200