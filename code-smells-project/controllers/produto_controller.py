"""Handlers de produtos."""
import logging

from flask import current_app, jsonify, request

from controllers.validators import validar_busca, validar_paginacao, validar_produto
from views.serializers import produto_publico

logger = logging.getLogger(__name__)


def _servico():
    return current_app.extensions["loja"].produto_service


def listar_produtos():
    limite, offset = validar_paginacao(request.args)
    produtos = _servico().listar(limite, offset)
    logger.info("Listando %d produtos", len(produtos))
    return jsonify({"dados": [produto_publico(p) for p in produtos], "sucesso": True}), 200


def buscar_produto(produto_id):
    return jsonify({"dados": produto_publico(_servico().obter(produto_id)), "sucesso": True}), 200


def buscar_produtos():
    filtros = validar_busca(request.args)
    resultados = _servico().buscar(**filtros)
    return jsonify({"dados": [produto_publico(p) for p in resultados], "total": len(resultados),
                    "sucesso": True}), 200


def criar_produto():
    dados = validar_produto(request.get_json(silent=True))
    produto_id = _servico().criar(dados)
    logger.info("Produto criado com ID %s", produto_id)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(produto_id):
    servico = _servico()
    servico.obter(produto_id)  # 404 antes da validação, como no comportamento original
    servico.atualizar(produto_id, validar_produto(request.get_json(silent=True)))
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(produto_id):
    _servico().excluir(produto_id)
    logger.info("Produto %s deletado", produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
