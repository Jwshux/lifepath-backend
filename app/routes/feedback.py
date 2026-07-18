from flask import Blueprint, request, jsonify

from ..models.feedback import create_feedback, get_all_feedback
from ..utils.security import decode_token

feedback_bp = Blueprint('feedback', __name__)


@feedback_bp.post('/')
def submit_feedback():
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()
    rating = data.get('rating')

    if not message:
        return jsonify({'error': 'Feedback message is required.'}), 400

    if rating is not None and not (1 <= int(rating) <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5.'}), 400

    # Optional: attach the feedback to a signed-in user if a valid token is sent.
    user_id = None
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1]
        user_id = decode_token(token)

    feedback_id = create_feedback(message, rating, user_id)

    return jsonify({
        'message': 'Feedback submitted successfully.',
        'id': str(feedback_id),
    }), 201


@feedback_bp.get('/')
def list_feedback():
    entries = get_all_feedback()
    return jsonify({'feedback': entries}), 200