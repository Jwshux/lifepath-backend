from flask import Flask

from .config import Config
from .extensions import bcrypt, cors, init_mongo, mail


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    bcrypt.init_app(app)
    mail.init_app(app)

    cors.init_app(
        app,
        origins=['http://localhost:3000'],
    )

    init_mongo(app)

    from .routes.auth import auth_bp
    from .routes.feedback import feedback_bp

    app.register_blueprint(
        auth_bp,
        url_prefix='/api/auth',
    )

    app.register_blueprint(
        feedback_bp,
        url_prefix='/api/feedback',
    )

    @app.get('/api/health')
    def health_check():
        return {'status': 'ok'}, 200

    return app