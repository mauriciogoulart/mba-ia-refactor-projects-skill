"""Constantes de domínio e regras de negócio."""
from decimal import Decimal

VERSAO_API = "1.0.0"

TIPO_ADMIN = "admin"
TIPO_CLIENTE = "cliente"

CATEGORIA_PADRAO = "geral"
CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]

NOME_PRODUTO_MIN = 2
NOME_PRODUTO_MAX = 200

STATUS_PENDENTE = "pendente"
STATUS_CANCELADO = "cancelado"
STATUS_PEDIDO_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]

# Faixas de desconto sobre o faturamento bruto: (limite exclusivo, taxa), da maior para a menor.
DESCONTOS_FATURAMENTO = (
    (Decimal("10000"), Decimal("0.10")),
    (Decimal("5000"), Decimal("0.05")),
    (Decimal("1000"), Decimal("0.02")),
)
