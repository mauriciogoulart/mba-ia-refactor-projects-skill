"""Acesso a dados de pedidos e itens (consultas parametrizadas, transação na criação)."""


class EstoqueInsuficiente(Exception):
    def __init__(self, nome_produto):
        super().__init__(nome_produto)
        self.nome_produto = nome_produto


class ProdutoInexistente(Exception):
    def __init__(self, produto_id):
        super().__init__(produto_id)
        self.produto_id = produto_id


class PedidoModel:
    def __init__(self, obter_conexao):
        self._conexao = obter_conexao

    def criar(self, usuario_id, itens, calcular_total):
        """Cria pedido, itens e baixa o estoque numa única transação.

        `itens`: lista de {"produto_id", "quantidade"}; `calcular_total(linhas)` recebe
        [(preco_unitario, quantidade)] e devolve o total. Qualquer erro desfaz tudo.
        """
        conexao = self._conexao()
        conexao.execute("BEGIN IMMEDIATE")
        try:
            linhas = []
            for item in itens:
                produto = conexao.execute(
                    "SELECT nome, preco FROM produtos WHERE id = ?", (item["produto_id"],)
                ).fetchone()
                if produto is None:
                    raise ProdutoInexistente(item["produto_id"])
                cursor = conexao.execute(
                    "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                    (item["quantidade"], item["produto_id"], item["quantidade"]),
                )
                if cursor.rowcount == 0:
                    raise EstoqueInsuficiente(produto["nome"])
                linhas.append((item["produto_id"], item["quantidade"], produto["preco"]))
            total = calcular_total([(preco, quantidade) for _, quantidade, preco in linhas])
            pedido_id = conexao.execute(
                "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
                (usuario_id, total),
            ).lastrowid
            conexao.executemany(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                [(pedido_id, produto_id, quantidade, preco) for produto_id, quantidade, preco in linhas],
            )
            conexao.commit()
        except Exception:
            conexao.rollback()
            raise
        return pedido_id, total

    def listar(self, usuario_id=None, limite=None, offset=0):
        sql = "SELECT id, usuario_id, status, total, criado_em FROM pedidos"
        parametros = []
        if usuario_id is not None:
            sql += " WHERE usuario_id = ?"
            parametros.append(usuario_id)
        sql += " ORDER BY id"
        if limite is not None:
            sql += " LIMIT ? OFFSET ?"
            parametros += [limite, offset]
        conexao = self._conexao()
        pedidos = [dict(linha) for linha in conexao.execute(sql, parametros).fetchall()]
        if not pedidos:
            return []
        ids = [p["id"] for p in pedidos]
        marcadores = ",".join("?" * len(ids))
        # Um único JOIN para os itens de todos os pedidos (sem N+1).
        itens = conexao.execute(
            f"""SELECT i.pedido_id, i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
                FROM itens_pedido i LEFT JOIN produtos pr ON pr.id = i.produto_id
                WHERE i.pedido_id IN ({marcadores}) ORDER BY i.id""",
            ids,
        ).fetchall()
        por_pedido = {p["id"]: [] for p in pedidos}
        for item in itens:
            por_pedido[item["pedido_id"]].append(dict(item))
        for pedido in pedidos:
            pedido["itens"] = por_pedido[pedido["id"]]
        return pedidos

    def atualizar_status(self, pedido_id, status):
        conexao = self._conexao()
        with conexao:
            cursor = conexao.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id))
        return cursor.rowcount > 0

    def resumo_vendas(self, status_contados):
        colunas = ", ".join("SUM(CASE WHEN status = ? THEN 1 ELSE 0 END)" for _ in status_contados)
        linha = self._conexao().execute(
            f"SELECT COUNT(*), COALESCE(SUM(total), 0), {colunas} FROM pedidos", list(status_contados)
        ).fetchone()
        total_pedidos, faturamento, *contagens = tuple(linha)
        return total_pedidos, faturamento, dict(zip(status_contados, (c or 0 for c in contagens)))

    def contar(self):
        return self._conexao().execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
