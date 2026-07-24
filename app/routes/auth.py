import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from flask import Blueprint, request, jsonify

from ..models.user import (
    find_user_by_email,
    find_user_by_username,
    create_user,
    save_password_reset_code,
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
            'If an account exists for that email, '
            'a password reset code has been sent.'
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