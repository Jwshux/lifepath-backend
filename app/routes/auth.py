import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from ..extensions import db
from itsdangerous import (
    URLSafeTimedSerializer,
    BadSignature,
    SignatureExpired,
)
from flask import current_app

from flask import Blueprint, request, jsonify

from ..models.user import (
    find_user_by_email,
    find_user_by_username,
    create_user,
    save_password_reset_code,
    clear_password_reset_code,
    update_user_password,
)
from ..utils.security import hash_password, check_password, generate_token
from ..utils.validators import is_valid_email, is_valid_password


auth_bp = Blueprint('auth', __name__)


@auth_bp.post('/signup')
def signup():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    username = (data.get('username') or '').strip()

    if not is_valid_email(email):
        return jsonify({'error': 'Please enter a valid email address.'}), 400

    if find_user_by_username(username):
        return jsonify({'error': 'Username is already taken.'}), 409

    if not is_valid_password(password):
        return jsonify({
            'error': (
                'Password must be 8 to 64 characters long '
                'and include at least one letter and one number.'
            )
        }), 400

    if not username:
        return jsonify({'error': 'Username is required.'}), 400

    if find_user_by_email(email):
        return jsonify({'error': 'An account with this email already exists.'}), 409

    hashed = hash_password(password)
    user_id = create_user(email, hashed, username)
    token = generate_token(user_id)

    return jsonify({
        'message': 'Account created successfully.',
        'token': token,
        'user': {'id': str(user_id), 'email': email, 'username': username},
    }), 201


@auth_bp.post('/signin')
def signin():
    data = request.get_json(silent=True) or {}

    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({
            'error': 'Username and password are required.'
        }), 400

    user = find_user_by_username(username)

    if not user or not check_password(password, user['password']):
        return jsonify({
            'error': 'Invalid username or password.'
        }), 401

    token = generate_token(user['_id'])

    return jsonify({
        'message': 'Signed in successfully.',
        'token': token,
        'user': {
            'id': str(user['_id']),
            'email': user['email'],
            'username': user['username'],
        },
    }), 200

@auth_bp.get('/check-username')
def check_username():
    username = (
        request.args.get('username') or ''
    ).strip()

    if len(username) < 3:
        return jsonify({
            'available': False,
            'message': 'Username must be at least 3 characters long.',
        }), 200

    user = find_user_by_username(username)

    return jsonify({
        'available': user is None,
        'message': (
            'Username available.'
            if user is None
            else 'Username already taken.'
        ),
    }), 200

@auth_bp.post('/forgot-password')
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()

    generic_response = {
        'message': (
            'Check your inbox for the 6-digit verification code.'
        )
    }

    if not is_valid_email(email):
        return jsonify(generic_response), 200

    user = find_user_by_email(email)

    if not user:
        return jsonify(generic_response), 200

    reset_code = f'{secrets.randbelow(1_000_000):06d}'

    reset_code_hash = hashlib.sha256(
        reset_code.encode('utf-8')
    ).hexdigest()

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=10)
    )

    save_password_reset_code(
        user['_id'],
        reset_code_hash,
        expires_at,
    )

    print(
        f'Password reset code for {email}: '
        f'{reset_code}'
    )

    return jsonify(generic_response), 200

@auth_bp.post('/verify-reset-code')
def verify_reset_code():
    data = request.get_json(silent=True) or {}

    email = (data.get('email') or '').strip().lower()
    reset_code = (data.get('code') or '').strip()

    if not email or not reset_code:
        return jsonify({
            'message': 'Email and reset code are required.'
        }), 400

    user = find_user_by_email(email)

    if not user:
        return jsonify({
            'message': 'Invalid or expired reset code.'
        }), 400

    stored_hash = user.get('password_reset_code_hash')
    expires_at = user.get('password_reset_expires_at')
    attempts = user.get('password_reset_attempts', 0)

    if not stored_hash or not expires_at:
        return jsonify({
            'message': 'Invalid or expired reset code.'
        }), 400
    
    if attempts >= 5:
        clear_password_reset_code(user['_id'])

        return jsonify({
            'message': 'Invalid or expired reset code.'
        }), 400

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expires_at:
        clear_password_reset_code(user['_id'])

        return jsonify({
            'message': 'Invalid or expired reset code.'
        }), 400

    submitted_hash = hashlib.sha256(
        reset_code.encode('utf-8')
    ).hexdigest()

    if submitted_hash != stored_hash:
        db.users.update_one(
            {'_id': user['_id']},
            {'$inc': {'password_reset_attempts': 1}},
        )

        return jsonify({
            'message': 'Invalid or expired reset code.'
        }), 400

    serializer = URLSafeTimedSerializer(
        current_app.config['SECRET_KEY']
    )

    reset_token = serializer.dumps(
        {
            'user_id': str(user['_id']),
            'purpose': 'password-reset',
        },
        salt='password-reset',
    )

    clear_password_reset_code(user['_id'])

    return jsonify({
        'message': 'Reset code verified.',
        'reset_token': reset_token,
    }), 200

@auth_bp.post('/reset-password')
def reset_password():
    data = request.get_json(silent=True) or {}

    reset_token = (data.get('reset_token') or '').strip()
    new_password = data.get('new_password') or ''

    if not reset_token or not new_password:
        return jsonify({
            'message': 'Reset token and new password are required.'
        }), 400

    if not is_valid_password(new_password):
        return jsonify({
            'message': (
                'Password must be 8 to 64 characters long '
                'and include at least one letter and one number.'
            )
        }), 400

    serializer = URLSafeTimedSerializer(
        current_app.config['SECRET_KEY']
    )

    try:
        token_data = serializer.loads(
            reset_token,
            salt='password-reset',
            max_age=600,
        )
    except SignatureExpired:
        return jsonify({
            'message': 'Password reset session has expired.'
        }), 400
    except BadSignature:
        return jsonify({
            'message': 'Invalid password reset session.'
        }), 400

    if token_data.get('purpose') != 'password-reset':
        return jsonify({
            'message': 'Invalid password reset session.'
        }), 400

    user_id = token_data.get('user_id')

    if not user_id:
        return jsonify({
            'message': 'Invalid password reset session.'
        }), 400

    hashed_password = hash_password(new_password)

    update_user_password(
        user_id,
        hashed_password,
    )

    return jsonify({
        'message': 'Password has been reset successfully.'
    }), 200