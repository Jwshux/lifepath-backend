from datetime import datetime, timezone
from bson import ObjectId
from ..extensions import db


def create_feedback(message, rating=None, user_id=None):
    entry = {
        'message': message,
        'rating': rating,
        'user_id': ObjectId(user_id) if user_id else None,
        'created_at': datetime.now(timezone.utc),
    }
    result = db.feedback.insert_one(entry)
    return result.inserted_id


def get_all_feedback():
    entries = db.feedback.find().sort('created_at', -1)

    feedback = []

    for entry in entries:
        user = None

        if entry.get('user_id'):
            user = db.users.find_one({
                '_id': entry['user_id']
            })

        feedback.append({
            'id': str(entry['_id']),
            'message': entry['message'],
            'rating': entry.get('rating'),
            'user_id': (
                str(entry['user_id'])
                if entry.get('user_id')
                else None
            ),
            'username': (
                user.get('username')
                if user
                else 'Anonymous'
            ),
            'created_at': (
                entry['created_at'].isoformat()
                if entry.get('created_at')
                else None
            ),
        })

    return feedback

def delete_feedback(feedback_id):
    try:
        object_id = ObjectId(feedback_id)
    except Exception:
        return False

    result = db.feedback.delete_one({
        '_id': object_id,
    })

    return result.deleted_count == 1