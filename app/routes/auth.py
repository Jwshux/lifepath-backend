from flask import Blueprint, request, jsonify

from ..models.user import (
    find_user_by_email,
    find_user_by_username,
    create_user,
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
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    user = find_user_by_email(email)

    # Same generic error whether the email doesn't exist or the password is
    # wrong — avoids revealing which emails are registered.
    if not user or not check_password(password, user['password']):
        return jsonify({'error': 'Invalid email or password.'}), 401

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