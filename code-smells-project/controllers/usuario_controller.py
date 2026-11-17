"""Handlers de usuários e login."""
import logging

from flask import current_app, jsonify, request

from controllers.validators import validar_login, validar_paginacao, validar_usuario
from middlewares.auth import garantir_proprio_ou_admin
from services.erros import AppError
from views.serializers import usuario_login, usuario_publico

logger = logging.getLogger(__name__)


def _loja():
    return current_app.extensions["loja"]


def listar_usuarios():
    limite, offset = validar_paginacao(request.args)
    usuarios = _loja().usuario_service.listar(limite, offset)
    return jsonify({"dados": [usuario_publico(u) for u in usuarios], "sucesso": True}), 200


def buscar_usuario(usuario_id):
    garantir_proprio_ou_admin(usuario_id)
    return jsonify({"dados": usuario_publico(_loja().usuario_service.obter(usuario_id)), "sucesso": True}), 200


def criar_usuario():
    dados = validar_usuario(request.get_json(silent=True))
    usuario_id = _loja().usuario_service.criar(dados["nome"], dados["email"], dados["senha"])
    logger.info("Usuário criado: id=%s", usuario_id)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    email, senha = validar_login(request.get_json(silent=True))
    loja = _loja()
    chave = f"{request.remote_addr}|{email.lower()}"
    if loja.limitador_login.bloqueado(chave):
        raise AppError("Muitas tentativas de login. Tente novamente mais tarde.", 429)
    usuario = loja.usuario_service.autenticar(email, senha)
    if usuario is None:
        loja.limitador_login.registrar_falha(chave)
        logger.info("Login falhou")
        raise AppError("Email ou senha inválidos", 401)
    loja.limitador_login.limpar(chave)
    logger.info("Login bem-sucedido: usuario_id=%s", usuario["id"])
    token = loja.token_service.emitir(usuario)
    return jsonify({"dados": usuario_login(usuario, token), "sucesso": True, "mensagem": "Login OK"}), 200
