from bson import ObjectId
from ..extensions import db


def find_user_by_email(email):
    return db.users.find_one({'email': email})


def find_user_by_id(user_id):
    try:
        return db.users.find_one({'_id': ObjectId(user_id)})
    except Exception:
        return None


def create_user(email, hashed_password, username):
    result = db.users.insert_one({
        'email': email,
        'password': hashed_password,
        'username': username,
    })
    return result.inserted_id