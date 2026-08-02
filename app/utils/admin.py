from functools import wraps

from flask import jsonify, request

from ..models.user import find_user_by_id
from .security import decode_token


def admin_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        authorization = request.headers.get(
            'Authorization',
            '',
        )

        if not authorization.startswith('Bearer '):
            return jsonify({
                'error': 'Authentication required.',
            }), 401

        token = authorization.removeprefix(
            'Bearer '
        ).strip()

        user_id = decode_token(token)

        if not user_id:
            return jsonify({
                'error': 'Invalid or expired token.',
            }), 401

        user = find_user_by_id(user_id)

        if not user:
            return jsonify({
                'error': 'User account not found.',
            }), 401

        if user.get('role', 'user') != 'admin':
            return jsonify({
                'error': 'Admin access required.',
            }), 403

        return view_function(
            *args,
            current_admin=user,
            **kwargs,
        )

    return wrapped_view