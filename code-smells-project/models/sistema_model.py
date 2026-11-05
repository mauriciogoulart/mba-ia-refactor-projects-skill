"""Consultas de sistema: contagens para health check e limpeza total do banco."""

_COMANDOS_LIMPEZA = (
    "DELETE FROM itens_pedido",
    "DELETE FROM pedidos",
    "DELETE FROM produtos",
    "DELETE FROM usuarios",
)


def contagens(db):
    linha = db.execute("""
        SELECT (SELECT COUNT(*) FROM produtos) AS produtos,
               (SELECT COUNT(*) FROM usuarios) AS usuarios,
               (SELECT COUNT(*) FROM pedidos) AS pedidos
    """).fetchone()
    return dict(linha)


def apagar_tudo(db):
    for comando in _COMANDOS_LIMPEZA:
        db.execute(comando)
