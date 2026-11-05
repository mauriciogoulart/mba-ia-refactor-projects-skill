"""Controller de pedidos."""
from flask import current_app, jsonify, request

import serializers
import validators


def _servico():
    return current_app.extensions["services"].pedidos


def criar():
    dados = validators.validar_novo_pedido(request.get_json(silent=True))
    resultado = _servico().criar(dados["usuario_id"], dados["itens"])
    return jsonify({
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso",
    }), 201


def listar_todos():
    pedidos = [serializers.pedido(p) for p in _servico().listar_todos()]
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_por_usuario(usuario_id):
    pedidos = [serializers.pedido(p) for p in _servico().listar_por_usuario(usuario_id)]
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status(pedido_id):
    novo_status = validators.validar_status_pedido(request.get_json(silent=True))
    _servico().atualizar_status(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
