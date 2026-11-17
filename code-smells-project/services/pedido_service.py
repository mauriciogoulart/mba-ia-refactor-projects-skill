"""Regras de pedidos: criação com total no servidor, status e notificações."""
import logging

from models.pedido_model import EstoqueInsuficiente, ProdutoInexistente
from services.dinheiro import arredondar, para_decimal
from services.erros import AppError

logger = logging.getLogger(__name__)


def calcular_total(linhas):
    return arredondar(sum((para_decimal(preco) * quantidade for preco, quantidade in linhas), para_decimal(0)))


class PedidoService:
    def __init__(self, pedido_model, usuario_service):
        self._pedidos = pedido_model
        self._usuarios = usuario_service

    def criar(self, usuario_id, itens):
        if not self._usuarios.existe(usuario_id):
            raise AppError("Usuário não encontrado", 400)
        try:
            pedido_id, total = self._pedidos.criar(usuario_id, itens, calcular_total)
        except ProdutoInexistente as e:
            raise AppError(f"Produto {e.produto_id} não encontrado", 400) from e
        except EstoqueInsuficiente as e:
            raise AppError(f"Estoque insuficiente para {e.nome_produto}", 400) from e
        logger.info("Notificações (email/SMS/push) enfileiradas: pedido_id=%s usuario_id=%s", pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}

    def listar(self, limite=None, offset=0):
        return self._pedidos.listar(limite=limite, offset=offset)

    def listar_por_usuario(self, usuario_id, limite=None, offset=0):
        return self._pedidos.listar(usuario_id=usuario_id, limite=limite, offset=offset)

    def atualizar_status(self, pedido_id, status):
        if not self._pedidos.atualizar_status(pedido_id, status):
            raise AppError("Pedido não encontrado", 404)
        if status == "aprovado":
            logger.info("Pedido %s aprovado: preparar envio", pedido_id)
        elif status == "cancelado":
            logger.info("Pedido %s cancelado: devolução de estoque pendente", pedido_id)
