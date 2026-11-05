"""Controller do relatório de vendas."""
from flask import current_app, jsonify


def vendas():
    relatorio = current_app.extensions["services"].relatorios.vendas()
    return jsonify({"dados": relatorio, "sucesso": True}), 200
