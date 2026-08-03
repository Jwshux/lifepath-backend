import os

from flask import Flask, jsonify

from .config import Config
from .extensions import (
    bcrypt,
    cors,
    init_mongo,
    limiter,
    mail,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    bcrypt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    cors.init_app(
        app,
        origins=[
            os.getenv(
                'FRONTEND_URL',
                'http://localhost:3000',
            )
        ],
        allow_headers=[
            'Content-Type',
            'Authorization',
        ],
        methods=[
            'GET',
            'POST',
            'PUT',
            'DELETE',
            'OPTIONS',
        ],
    )
    
    init_mongo(app)

    from .routes.admin import admin_bp
    from .routes.auth import auth_bp
    from .routes.feedback import feedback_bp
    from .routes.releases import releases_bp

    app.register_blueprint(
        auth_bp,
        url_prefix='/api/auth',
    )

    app.register_blueprint(
        feedback_bp,
        url_prefix='/api/feedback',
    )

    app.register_blueprint(
        admin_bp,
        url_prefix='/api/admin',
    )

    app.register_blueprint(
        releases_bp,
        url_prefix='/api/releases',
    )

    @app.get('/api/health')
    def health_check():
        return {'status': 'ok'}, 200

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': (
                'Download limit reached. '
                'Please try again later.'
            ),
        }), 429

    return app