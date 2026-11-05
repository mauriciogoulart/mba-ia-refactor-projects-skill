"""Acesso a dados de pedidos e itens. A transação é do chamador (service)."""

_SELECT_PEDIDOS_COM_ITENS = """
    SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
           i.produto_id, COALESCE(pr.nome, 'Desconhecido') AS produto_nome,
           i.quantidade, i.preco_unitario
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
"""


def inserir(db, usuario_id, status, total):
    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
        (usuario_id, status, total),
    )
    return cursor.lastrowid


def inserir_item(db, pedido_id, produto_id, quantidade, preco_unitario):
    db.execute(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
        (pedido_id, produto_id, quantidade, preco_unitario),
    )


def obter(db, pedido_id):
    linha = db.execute(
        "SELECT id, usuario_id, status, total, criado_em FROM pedidos WHERE id = ?", (pedido_id,)
    ).fetchone()
    return dict(linha) if linha else None


def listar_itens(db, pedido_id):
    linhas = db.execute(
        "SELECT produto_id, quantidade FROM itens_pedido WHERE pedido_id = ?", (pedido_id,)
    ).fetchall()
    return [dict(linha) for linha in linhas]


def atualizar_status(db, pedido_id, status):
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id))


def listar_com_itens(db, usuario_id=None):
    """Pedidos com seus itens em uma única consulta (sem N+1), na ordem de criação."""
    sql = _SELECT_PEDIDOS_COM_ITENS
    parametros = []
    if usuario_id is not None:
        sql += " WHERE p.usuario_id = ?"
        parametros.append(usuario_id)
    sql += " ORDER BY p.id, i.id"

    pedidos = {}
    for linha in db.execute(sql, parametros).fetchall():
        pedido = pedidos.setdefault(linha["id"], {
            "id": linha["id"],
            "usuario_id": linha["usuario_id"],
            "status": linha["status"],
            "total": linha["total"],
            "criado_em": linha["criado_em"],
            "itens": [],
        })
        if linha["produto_id"] is not None:
            pedido["itens"].append({
                "produto_id": linha["produto_id"],
                "produto_nome": linha["produto_nome"],
                "quantidade": linha["quantidade"],
                "preco_unitario": linha["preco_unitario"],
            })
    return list(pedidos.values())


def resumo_vendas(db):
    linha = db.execute("""
        SELECT COUNT(*) AS total_pedidos,
               COALESCE(SUM(total), 0) AS faturamento,
               COALESCE(SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END), 0) AS pendentes,
               COALESCE(SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END), 0) AS aprovados,
               COALESCE(SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END), 0) AS cancelados
        FROM pedidos
    """).fetchone()
    return dict(linha)
