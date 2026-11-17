"""Handlers de pedidos."""
from flask import current_app, jsonify, request

from controllers.validators import validar_paginacao, validar_pedido, validar_status
from middlewares.auth import garantir_proprio_ou_admin
from views.serializers import pedido_publico


def _servico():
    return current_app.extensions["loja"].pedido_service


def criar_pedido():
    usuario_id, itens = validar_pedido(request.get_json(silent=True))
    garantir_proprio_ou_admin(usuario_id)
    resultado = _servico().criar(usuario_id, itens)
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_pedidos_usuario(usuario_id):
    garantir_proprio_ou_admin(usuario_id)
    limite, offset = validar_paginacao(request.args)
    pedidos = _servico().listar_por_usuario(usuario_id, limite, offset)
    return jsonify({"dados": [pedido_publico(p) for p in pedidos], "sucesso": True}), 200


def listar_todos_pedidos():
    limite, offset = validar_paginacao(request.args)
    pedidos = _servico().listar(limite, offset)
    return jsonify({"dados": [pedido_publico(p) for p in pedidos], "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    _servico().atualizar_status(pedido_id, validar_status(request.get_json(silent=True)))
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
