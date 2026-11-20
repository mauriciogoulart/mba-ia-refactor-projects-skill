"""Cálculo monetário em Decimal (armazenamento continua REAL; conversão na borda)."""
from decimal import ROUND_HALF_UP, Decimal

from services.regras import CENTAVOS


def para_decimal(valor):
    return Decimal(str(valor))


def arredondar(valor):
    return float(para_decimal(valor).quantize(CENTAVOS, rounding=ROUND_HALF_UP))
