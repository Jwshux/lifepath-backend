import datetime

import jwt
from flask import current_app

from ..extensions import bcrypt


def hash_password(plain_password):
    return bcrypt.generate_password_hash(
        plain_password
    ).decode('utf-8')


def check_password(plain_password, hashed_password):
    return bcrypt.check_password_hash(
        hashed_password,
        plain_password,
    )


def generate_token(user_id):
    now = datetime.datetime.now(datetime.timezone.utc)

    payload = {
        'user_id': str(user_id),
        'iat': now,
        'exp': now + datetime.timedelta(days=7),
    }

    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256',
    )


def decode_token(token):
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256'],
        )

        return payload.get('user_id')

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None