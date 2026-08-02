from bson import ObjectId
from ..extensions import db


def find_user_by_email(email):
    return db.users.find_one({'email': email})


def find_user_by_id(user_id):
    try:
        return db.users.find_one({'_id': ObjectId(user_id)})
    except Exception:
        return None

def find_user_by_username(username):
    return db.users.find_one({'username': username})

def create_user(email, hashed_password, username):
    result = db.users.insert_one({
        'email': email,
        'password': hashed_password,
        'username': username,
        'role': 'user',
    })
    return result.inserted_id

def save_password_reset_code(user_id, reset_code_hash, expires_at):
    db.users.update_one(
        {'_id': user_id},
        {
            '$set': {
                'password_reset_code_hash': reset_code_hash,
                'password_reset_expires_at': expires_at,
                'password_reset_attempts': 0,
            }
        },
    )

def clear_password_reset_code(user_id):
    db.users.update_one(
        {'_id': user_id},
        {
            '$unset': {
                'password_reset_code_hash': '',
                'password_reset_expires_at': '',
                'password_reset_attempts': '',
            }
        },
    )

def update_user_password(user_id, hashed_password):
    db.users.update_one(
        {'_id': ObjectId(user_id)},
        {
            '$set': {
                'password': hashed_password,
            }
        },
    )