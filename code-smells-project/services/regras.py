"""Constantes de regra de negócio."""
from decimal import Decimal

CATEGORIAS_VALIDAS = ("informatica", "moveis", "vestuario", "geral", "eletronicos", "livros")
CATEGORIA_PADRAO = "geral"
NOME_PRODUTO_MIN, NOME_PRODUTO_MAX = 2, 200

STATUS_PEDIDO = ("pendente", "aprovado", "enviado", "entregue", "cancelado")
STATUS_RELATORIO = ("pendente", "aprovado", "cancelado")

TIPO_ADMIN = "admin"
TIPO_CLIENTE = "cliente"

# (faturamento acima de, percentual de desconto), da maior faixa para a menor
FAIXAS_DESCONTO = (
    (Decimal("10000"), Decimal("0.10")),
    (Decimal("5000"), Decimal("0.05")),
    (Decimal("1000"), Decimal("0.02")),
)

CENTAVOS = Decimal("0.01")
