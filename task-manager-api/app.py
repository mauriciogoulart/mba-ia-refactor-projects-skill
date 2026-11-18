import logging

from flask import Flask
from flask_cors import CORS

from config.settings import load_settings
from database import db
from middleware.error_handler import register_error_handlers
from middleware.security import LoginThrottle, register_security_headers
from routes.category_routes import category_bp
from routes.report_routes import report_bp
from routes.system_routes import system_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from services.token_service import TokenService


def create_app(settings=None):
    settings = settings or load_settings()
    logging.basicConfig(level=settings.LOG_LEVEL, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = settings.SECRET_KEY

    app.extensions['token_service'] = TokenService(settings.SECRET_KEY, settings.TOKEN_MAX_AGE_SECONDS)
    app.extensions['login_throttle'] = LoginThrottle(settings.LOGIN_MAX_FAILURES, settings.LOGIN_WINDOW_SECONDS)

    if settings.CORS_ORIGINS:
        CORS(app, origins=settings.CORS_ORIGINS)
    db.init_app(app)

    for blueprint in (system_bp, task_bp, user_bp, category_bp, report_bp):
        app.register_blueprint(blueprint)
    register_error_handlers(app)
    register_security_headers(app)

    with app.app_context():
        db.create_all()
    return app


if __name__ == '__main__':
    app_settings = load_settings()
    create_app(app_settings).run(debug=app_settings.DEBUG, host=app_settings.HOST, port=app_settings.PORT)
