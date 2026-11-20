"""Saúde da aplicação e operações administrativas."""
import logging

logger = logging.getLogger(__name__)


class SistemaService:
    def __init__(self, produto_model, usuario_model, pedido_model, admin_model):
        self._produtos = produto_model
        self._usuarios = usuario_model
        self._pedidos = pedido_model
        self._admin = admin_model

    def contagens(self):
        return {
            "produtos": self._produtos.contar(),
            "usuarios": self._usuarios.contar(),
            "pedidos": self._pedidos.contar(),
        }

    def resetar_banco(self, admin_id):
        self._admin.limpar_tabelas()
        logger.warning("Banco de dados resetado pelo administrador id=%s", admin_id)
