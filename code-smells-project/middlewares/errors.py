"""Tratamento central de erros: formato único e sem detalhe interno para o cliente."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from services.erros import AppError

logger = logging.getLogger(__name__)


def resposta_erro(mensagem, status):
    return jsonify({"erro": mensagem, "sucesso": False}), status


def registrar_handlers_de_erro(app):
    @app.errorhandler(AppError)
    def _erro_de_dominio(e):
        return resposta_erro(e.mensagem, e.status)

    @app.errorhandler(HTTPException)
    def _erro_http(e):
        return e  # 404/405 de roteamento mantêm a resposta padrão do Flask

    @app.errorhandler(Exception)
    def _erro_inesperado(e):
        logger.exception("Erro não tratado")
        return resposta_erro("Erro interno", 500)
