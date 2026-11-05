"""Tratamento central de erros: formato único e sem vazar detalhes internos."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from errors import AppError

logger = logging.getLogger(__name__)


def registrar_tratadores_de_erro(app):
    @app.errorhandler(AppError)
    def _tratar_erro_de_dominio(erro):
        return jsonify({"erro": erro.message, "sucesso": False}), erro.status

    @app.errorhandler(Exception)
    def _tratar_erro_inesperado(erro):
        if isinstance(erro, HTTPException):
            return erro
        logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
