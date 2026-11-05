"""Controller de usuários e login."""
from flask import current_app, jsonify, request

import serializers
import validators
from middlewares.auth import emitir_token


def _servico():
    return current_app.extensions["services"].usuarios


def listar():
    usuarios = [serializers.usuario(u) for u in _servico().listar()]
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar_por_id(usuario_id):
    usuario = _servico().obter(usuario_id)
    return jsonify({"dados": serializers.usuario(usuario), "sucesso": True}), 200


def criar():
    dados = validators.validar_novo_usuario(request.get_json(silent=True))
    usuario_id = _servico().criar(dados)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    credenciais = validators.validar_login(request.get_json(silent=True))
    usuario = _servico().autenticar(credenciais["email"], credenciais["senha"])
    return jsonify({
        "dados": serializers.usuario_login(usuario),
        "token": emitir_token(usuario),
        "sucesso": True,
        "mensagem": "Login OK",
    }), 200
