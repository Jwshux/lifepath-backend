from datetime import datetime, timezone

from pymongo import ReturnDocument

from ..extensions import db


def serialize_release(release):
    if not release:
        return None

    uploaded_at = release.get('uploaded_at')

    return {
        'id': str(release['_id']),
        'version': release.get('version'),
        'android_requirement': release.get(
            'android_requirement'
        ),
        'release_notes': release.get(
            'release_notes',
            '',
        ),
        'file_name': release.get('file_name'),
        'file_size': release.get('file_size'),
        'object_key': release.get('object_key'),
        'sha256': release.get('sha256'),
        'uploaded_by': (
            str(release['uploaded_by'])
            if release.get('uploaded_by')
            else None
        ),
        'uploaded_at': (
            uploaded_at.replace(
                tzinfo=timezone.utc
            ).isoformat()
            if uploaded_at and uploaded_at.tzinfo is None
            else uploaded_at.isoformat()
            if uploaded_at
            else None
        ),
    }


def get_current_release():
    release = db.releases.find_one({
        '_id': 'current',
    })

    return serialize_release(release)


def replace_current_release(
    version,
    android_requirement,
    release_notes,
    file_name,
    file_size,
    object_key,
    sha256,
    uploaded_by,
):
    new_release = {
        'version': version,
        'android_requirement': android_requirement,
        'release_notes': release_notes,
        'file_name': file_name,
        'file_size': file_size,
        'object_key': object_key,
        'sha256': sha256,
        'uploaded_by': uploaded_by,
        'uploaded_at': datetime.now(timezone.utc),
    }

    previous_release = db.releases.find_one_and_update(
        {
            '_id': 'current',
        },
        {
            '$set': new_release,
        },
        upsert=True,
        return_document=ReturnDocument.BEFORE,
    )

    current_release = {
        '_id': 'current',
        **new_release,
    }

    return (
        serialize_release(current_release),
        serialize_release(previous_release),
    )