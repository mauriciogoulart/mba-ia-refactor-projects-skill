"""Relatório de vendas com cálculo monetário exato (Decimal)."""
from decimal import ROUND_HALF_UP, Decimal

from constants import DESCONTOS_FATURAMENTO
from models import pedido_model

_CENTAVOS = Decimal("0.01")


def _moeda(valor):
    return float(valor.quantize(_CENTAVOS, rounding=ROUND_HALF_UP))


def _taxa_desconto(faturamento):
    for limite, taxa in DESCONTOS_FATURAMENTO:
        if faturamento > limite:
            return taxa
    return Decimal(0)


class RelatorioService:
    def __init__(self, obter_db):
        self._obter_db = obter_db

    def vendas(self):
        resumo = pedido_model.resumo_vendas(self._obter_db())
        total_pedidos = resumo["total_pedidos"]
        faturamento = Decimal(str(resumo["faturamento"]))
        desconto = faturamento * _taxa_desconto(faturamento)

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": _moeda(faturamento),
            "desconto_aplicavel": _moeda(desconto),
            "faturamento_liquido": _moeda(faturamento - desconto),
            "pedidos_pendentes": resumo["pendentes"],
            "pedidos_aprovados": resumo["aprovados"],
            "pedidos_cancelados": resumo["cancelados"],
            "ticket_medio": _moeda(faturamento / total_pedidos) if total_pedidos > 0 else 0,
        }
