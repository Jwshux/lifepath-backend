from functools import wraps

from flask import jsonify, request

from ..models.user import find_user_by_id
from ..utils.security import decode_token


def user_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        authorization = request.headers.get(
            'Authorization',
            '',
        )

        if not authorization.startswith('Bearer '):
            return jsonify({
                'error': 'Authentication is required.',
            }), 401

        token = authorization.split(' ', 1)[1].strip()

        if not token:
            return jsonify({
                'error': 'Authentication is required.',
            }), 401

        user_id = decode_token(token)

        if not user_id:
            return jsonify({
                'error': 'Invalid or expired token.',
            }), 401

        current_user = find_user_by_id(user_id)

        if not current_user:
            return jsonify({
                'error': 'User account not found.',
            }), 401

        return view_function(
            current_user,
            *args,
            **kwargs,
        )

    return wrapped_view