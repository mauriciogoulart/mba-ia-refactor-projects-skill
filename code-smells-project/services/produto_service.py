"""Regras de negócio de produtos."""
import logging
import sqlite3

from errors import AppError
from models import produto_model

logger = logging.getLogger(__name__)


class ProdutoService:
    def __init__(self, obter_db):
        self._obter_db = obter_db

    def listar(self):
        return produto_model.listar(self._obter_db())

    def obter(self, produto_id):
        produto = produto_model.obter(self._obter_db(), produto_id)
        if produto is None:
            raise AppError("Produto não encontrado", 404)
        return produto

    def buscar(self, termo, categoria, preco_min, preco_max):
        return produto_model.buscar(self._obter_db(), termo, categoria, preco_min, preco_max)

    def criar(self, dados):
        db = self._obter_db()
        produto_id = produto_model.criar(
            db, dados["nome"], dados["descricao"], dados["preco"], dados["estoque"], dados["categoria"]
        )
        db.commit()
        logger.info("Produto criado id=%s", produto_id)
        return produto_id

    def atualizar(self, produto_id, dados):
        self.obter(produto_id)
        db = self._obter_db()
        produto_model.atualizar(
            db, produto_id, dados["nome"], dados["descricao"], dados["preco"],
            dados["estoque"], dados["categoria"],
        )
        db.commit()

    def deletar(self, produto_id):
        self.obter(produto_id)
        db = self._obter_db()
        if produto_model.possui_pedidos(db, produto_id):
            raise AppError("Produto possui pedidos associados e não pode ser removido", 409)
        try:
            produto_model.deletar(db, produto_id)
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            raise AppError("Produto possui pedidos associados e não pode ser removido", 409)
        logger.info("Produto removido id=%s", produto_id)
