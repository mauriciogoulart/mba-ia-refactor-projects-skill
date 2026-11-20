"""Acesso a dados de produtos (consultas parametrizadas)."""

COLUNAS = "id, nome, descricao, preco, estoque, categoria, ativo, criado_em"


class ProdutoModel:
    def __init__(self, obter_conexao):
        self._conexao = obter_conexao

    def listar(self, limite=None, offset=0):
        sql = f"SELECT {COLUNAS} FROM produtos ORDER BY id"
        parametros = []
        if limite is not None:
            sql += " LIMIT ? OFFSET ?"
            parametros = [limite, offset]
        return [dict(linha) for linha in self._conexao().execute(sql, parametros).fetchall()]

    def obter(self, produto_id):
        linha = self._conexao().execute(
            f"SELECT {COLUNAS} FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
        return dict(linha) if linha else None

    def buscar(self, termo=None, categoria=None, preco_min=None, preco_max=None):
        condicoes, parametros = [], []
        if termo:
            condicoes.append("(nome LIKE ? OR descricao LIKE ?)")
            parametros += [f"%{termo}%", f"%{termo}%"]
        if categoria:
            condicoes.append("categoria = ?")
            parametros.append(categoria)
        if preco_min is not None:
            condicoes.append("preco >= ?")
            parametros.append(preco_min)
        if preco_max is not None:
            condicoes.append("preco <= ?")
            parametros.append(preco_max)
        where = (" WHERE " + " AND ".join(condicoes)) if condicoes else ""
        sql = f"SELECT {COLUNAS} FROM produtos{where} ORDER BY id"
        return [dict(linha) for linha in self._conexao().execute(sql, parametros).fetchall()]

    def criar(self, nome, descricao, preco, estoque, categoria):
        conexao = self._conexao()
        with conexao:
            cursor = conexao.execute(
                "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
                (nome, descricao, preco, estoque, categoria),
            )
        return cursor.lastrowid

    def atualizar(self, produto_id, nome, descricao, preco, estoque, categoria):
        conexao = self._conexao()
        with conexao:
            cursor = conexao.execute(
                "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
                (nome, descricao, preco, estoque, categoria, produto_id),
            )
        return cursor.rowcount > 0

    def excluir(self, produto_id):
        conexao = self._conexao()
        with conexao:
            cursor = conexao.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        return cursor.rowcount > 0

    def contar(self):
        return self._conexao().execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
