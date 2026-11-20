"""Relatório de vendas: agregação e faixas de desconto."""
from services.dinheiro import arredondar, para_decimal
from services.regras import FAIXAS_DESCONTO, STATUS_RELATORIO


def calcular_desconto(faturamento):
    faturamento = para_decimal(faturamento)
    for limite, percentual in FAIXAS_DESCONTO:
        if faturamento > limite:
            return faturamento * percentual
    return para_decimal(0)


class RelatorioService:
    def __init__(self, pedido_model):
        self._pedidos = pedido_model

    def vendas(self):
        total_pedidos, faturamento, por_status = self._pedidos.resumo_vendas(STATUS_RELATORIO)
        faturamento = para_decimal(faturamento)
        desconto = calcular_desconto(faturamento)
        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": arredondar(faturamento),
            "desconto_aplicavel": arredondar(desconto),
            "faturamento_liquido": arredondar(faturamento - desconto),
            "pedidos_pendentes": por_status["pendente"],
            "pedidos_aprovados": por_status["aprovado"],
            "pedidos_cancelados": por_status["cancelado"],
            "ticket_medio": arredondar(faturamento / total_pedidos) if total_pedidos > 0 else 0,
        }
