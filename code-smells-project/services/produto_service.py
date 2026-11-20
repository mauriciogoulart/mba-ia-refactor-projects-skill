"""Regras de produtos."""
from services.erros import AppError


class ProdutoService:
    def __init__(self, produto_model):
        self._produtos = produto_model

    def listar(self, limite=None, offset=0):
        return self._produtos.listar(limite, offset)

    def obter(self, produto_id):
        produto = self._produtos.obter(produto_id)
        if produto is None:
            raise AppError("Produto não encontrado", 404)
        return produto

    def buscar(self, termo, categoria, preco_min, preco_max):
        return self._produtos.buscar(termo, categoria, preco_min, preco_max)

    def criar(self, dados):
        return self._produtos.criar(dados["nome"], dados["descricao"], dados["preco"],
                                    dados["estoque"], dados["categoria"])

    def atualizar(self, produto_id, dados):
        if not self._produtos.atualizar(produto_id, dados["nome"], dados["descricao"], dados["preco"],
                                        dados["estoque"], dados["categoria"]):
            raise AppError("Produto não encontrado", 404)

    def excluir(self, produto_id):
        if not self._produtos.excluir(produto_id):
            raise AppError("Produto não encontrado", 404)
