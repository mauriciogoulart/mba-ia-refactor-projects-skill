"""Acesso a dados de usuários (consultas parametrizadas).

As funções devolvem o registro interno, incluindo o hash da senha; a serialização
pública (sem a senha) fica em views/serializers.py.
"""

COLUNAS = "id, nome, email, senha, tipo, criado_em"


class UsuarioModel:
    def __init__(self, obter_conexao):
        self._conexao = obter_conexao

    def listar(self, limite=None, offset=0):
        sql = f"SELECT {COLUNAS} FROM usuarios ORDER BY id"
        parametros = []
        if limite is not None:
            sql += " LIMIT ? OFFSET ?"
            parametros = [limite, offset]
        return [dict(linha) for linha in self._conexao().execute(sql, parametros).fetchall()]

    def obter(self, usuario_id):
        linha = self._conexao().execute(
            f"SELECT {COLUNAS} FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        return dict(linha) if linha else None

    def obter_por_email(self, email):
        linha = self._conexao().execute(
            f"SELECT {COLUNAS} FROM usuarios WHERE email = ? ORDER BY id LIMIT 1", (email,)
        ).fetchone()
        return dict(linha) if linha else None

    def criar(self, nome, email, senha_hash, tipo="cliente"):
        conexao = self._conexao()
        with conexao:
            cursor = conexao.execute(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                (nome, email, senha_hash, tipo),
            )
        return cursor.lastrowid

    def atualizar_senha(self, usuario_id, senha_hash):
        conexao = self._conexao()
        with conexao:
            conexao.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (senha_hash, usuario_id))

    def contar(self):
        return self._conexao().execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
