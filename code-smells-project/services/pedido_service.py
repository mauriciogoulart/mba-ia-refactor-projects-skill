"""Regras de negócio de pedidos: total, estoque atômico, transação e cancelamento."""
from decimal import ROUND_HALF_UP, Decimal

from constants import STATUS_CANCELADO, STATUS_PENDENTE
from errors import AppError
from models import pedido_model, produto_model
from services import notificacao_service

_CENTAVOS = Decimal("0.01")


def _moeda(valor):
    return valor.quantize(_CENTAVOS, rounding=ROUND_HALF_UP)


class PedidoService:
    def __init__(self, obter_db, usuario_service):
        self._obter_db = obter_db
        self._usuarios = usuario_service

    def listar_todos(self):
        return pedido_model.listar_com_itens(self._obter_db())

    def listar_por_usuario(self, usuario_id):
        return pedido_model.listar_com_itens(self._obter_db(), usuario_id)

    def criar(self, usuario_id, itens):
        db = self._obter_db()
        if not self._usuarios.existe(usuario_id):
            raise AppError("Usuário " + str(usuario_id) + " não encontrado")

        total = Decimal(0)
        precos = {}
        for item in itens:
            produto = produto_model.obter(db, item["produto_id"])
            if produto is None:
                raise AppError("Produto " + str(item["produto_id"]) + " não encontrado")
            if produto["estoque"] < item["quantidade"]:
                raise AppError("Estoque insuficiente para " + produto["nome"])
            preco = Decimal(str(produto["preco"]))
            precos[item["produto_id"]] = produto["preco"]
            total += preco * item["quantidade"]
        total = float(_moeda(total))

        try:
            pedido_id = pedido_model.inserir(db, usuario_id, STATUS_PENDENTE, total)
            for item in itens:
                if not produto_model.baixar_estoque(db, item["produto_id"], item["quantidade"]):
                    produto = produto_model.obter(db, item["produto_id"])
                    raise AppError("Estoque insuficiente para " + produto["nome"])
                pedido_model.inserir_item(
                    db, pedido_id, item["produto_id"], item["quantidade"], precos[item["produto_id"]]
                )
            db.commit()
        except Exception:
            db.rollback()
            raise

        notificacao_service.pedido_criado(pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}

    def atualizar_status(self, pedido_id, novo_status):
        db = self._obter_db()
        pedido = pedido_model.obter(db, pedido_id)
        if pedido is None:
            raise AppError("Pedido não encontrado", 404)

        try:
            if novo_status == STATUS_CANCELADO and pedido["status"] != STATUS_CANCELADO:
                for item in pedido_model.listar_itens(db, pedido_id):
                    produto_model.repor_estoque(db, item["produto_id"], item["quantidade"])
            pedido_model.atualizar_status(db, pedido_id, novo_status)
            db.commit()
        except Exception:
            db.rollback()
            raise

        notificacao_service.status_alterado(pedido_id, novo_status)
