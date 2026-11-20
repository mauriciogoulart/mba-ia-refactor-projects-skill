"""Handlers de raiz, saúde, relatório e administração."""
import logging

from flask import current_app, g, jsonify

logger = logging.getLogger(__name__)

VERSAO_API = "1.0.0"


def _loja():
    return current_app.extensions["loja"]


def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": VERSAO_API,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


def health_check():
    try:
        contagens = _loja().sistema_service.contagens()
    except Exception:
        logger.exception("Falha no health check")
        return jsonify({"status": "erro", "detalhes": "Banco de dados indisponível"}), 500
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": contagens,
        "versao": VERSAO_API,
        "ambiente": current_app.config["AMBIENTE"],
    }), 200


def relatorio_vendas():
    return jsonify({"dados": _loja().relatorio_service.vendas(), "sucesso": True}), 200


def reset_database():
    _loja().sistema_service.resetar_banco(g.usuario["id"])
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
