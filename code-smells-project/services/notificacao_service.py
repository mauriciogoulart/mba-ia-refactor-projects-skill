"""Notificações (hoje apenas registradas em log; sem integração externa)."""
import logging

logger = logging.getLogger(__name__)


def pedido_criado(pedido_id, usuario_id):
    logger.info("Notificação (e-mail/SMS/push): pedido %s criado para usuario %s", pedido_id, usuario_id)


def status_alterado(pedido_id, status):
    if status == "aprovado":
        logger.info("Pedido %s aprovado; preparar envio", pedido_id)
    elif status == "cancelado":
        logger.info("Pedido %s cancelado; estoque devolvido", pedido_id)
