"""Controller de produtos: valida o formato, chama o service e escolhe a resposta."""
from flask import current_app, jsonify, request

import serializers
import validators


def _servico():
    return current_app.extensions["services"].produtos


def listar():
    produtos = [serializers.produto(p) for p in _servico().listar()]
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_por_id(produto_id):
    produto = _servico().obter(produto_id)
    return jsonify({"dados": serializers.produto(produto), "sucesso": True}), 200


def buscar():
    termo, categoria, preco_min, preco_max = validators.validar_filtros_busca(request.args)
    resultados = [serializers.produto(p) for p in _servico().buscar(termo, categoria, preco_min, preco_max)]
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


def criar():
    dados = validators.validar_produto(request.get_json(silent=True))
    produto_id = _servico().criar(dados)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar(produto_id):
    _servico().obter(produto_id)
    dados = validators.validar_produto(request.get_json(silent=True))
    _servico().atualizar(produto_id, dados)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar(produto_id):
    _servico().deletar(produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
