"""Tratamento central de erros: formato único {'error': ...}, sem detalhes internos ao cliente."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from database import db
from services.exceptions import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({'error': error.message}), error.status

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        if isinstance(error, HTTPException):
            return error
        db.session.rollback()
        logger.exception("Erro não tratado")
        return jsonify({'error': 'Erro interno'}), 500
