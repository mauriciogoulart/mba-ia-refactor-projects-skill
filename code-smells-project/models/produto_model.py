"""Acesso a dados de produtos. Todas as consultas são parametrizadas; a transação é do chamador."""

_SELECT = "SELECT id, nome, descricao, preco, estoque, categoria, ativo, criado_em FROM produtos"


def listar(db):
    return [dict(linha) for linha in db.execute(_SELECT).fetchall()]


def obter(db, produto_id):
    linha = db.execute(_SELECT + " WHERE id = ?", (produto_id,)).fetchone()
    return dict(linha) if linha else None


def buscar(db, termo, categoria=None, preco_min=None, preco_max=None):
    sql = _SELECT + " WHERE 1=1"
    parametros = []
    if termo:
        sql += " AND (nome LIKE ? OR descricao LIKE ?)"
        padrao = "%" + termo + "%"
        parametros.extend([padrao, padrao])
    if categoria:
        sql += " AND categoria = ?"
        parametros.append(categoria)
    if preco_min is not None:
        sql += " AND preco >= ?"
        parametros.append(preco_min)
    if preco_max is not None:
        sql += " AND preco <= ?"
        parametros.append(preco_max)
    return [dict(linha) for linha in db.execute(sql, parametros).fetchall()]


def criar(db, nome, descricao, preco, estoque, categoria):
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    return cursor.lastrowid


def atualizar(db, produto_id, nome, descricao, preco, estoque, categoria):
    db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )


def deletar(db, produto_id):
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))


def possui_pedidos(db, produto_id):
    linha = db.execute(
        "SELECT 1 FROM itens_pedido WHERE produto_id = ? LIMIT 1", (produto_id,)
    ).fetchone()
    return linha is not None


def baixar_estoque(db, produto_id, quantidade):
    """Baixa atômica: só altera se houver estoque suficiente. Retorna True se baixou."""
    cursor = db.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
        (quantidade, produto_id, quantidade),
    )
    return cursor.rowcount == 1


def repor_estoque(db, produto_id, quantidade):
    db.execute(
        "UPDATE produtos SET estoque = estoque + ? WHERE id = ?", (quantidade, produto_id)
    )
