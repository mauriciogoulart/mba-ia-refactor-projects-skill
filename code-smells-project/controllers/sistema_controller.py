"""Controller de sistema: raiz, health check e reset administrativo."""
from flask import current_app, jsonify

from constants import VERSAO_API


def raiz():
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


def health():
    contagens = current_app.extensions["services"].sistema.contagens()
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": contagens,
        "versao": VERSAO_API,
        "ambiente": current_app.config["AMBIENTE"],
    }), 200


def resetar_banco():
    current_app.extensions["services"].sistema.resetar_banco()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
