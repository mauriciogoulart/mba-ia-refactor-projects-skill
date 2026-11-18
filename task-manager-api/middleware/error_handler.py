import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from utils.errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({'error': error.message}), error.status

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        if error.code is None or error.code < 400:
            return error
        return jsonify({'error': error.name}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception('Erro não tratado')
        return jsonify({'error': 'Erro interno'}), 500
