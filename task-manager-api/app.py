"""Composition root: cria a aplicação, injeta dependências e inicia o servidor."""
import logging

from flask import Flask

from config.logging_config import configure_logging
from config.settings import Settings
from database import db
from middlewares.error_handler import register_error_handlers
from middlewares.security import register_security
from routes import register_blueprints
from services.auth_service import TokenSigner

logger = logging.getLogger(__name__)


def create_app(settings=None):
    settings = settings or Settings.from_env()
    configure_logging(settings.LOG_LEVEL)
    if not settings.SECRET_KEY_FROM_ENV:
        logger.warning("SECRET_KEY não definida: usando chave aleatória (tokens expiram a cada reinício)")

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.extensions['token_signer'] = TokenSigner(settings.SECRET_KEY, settings.TOKEN_MAX_AGE)

    db.init_app(app)
    register_security(app, settings)
    register_error_handlers(app)
    register_blueprints(app)

    with app.app_context():
        db.create_all()
    return app


if __name__ == '__main__':
    settings = Settings.from_env()
    create_app(settings).run(debug=settings.DEBUG, host=settings.HOST, port=settings.PORT)
