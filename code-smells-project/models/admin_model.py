"""Operações administrativas sobre o banco."""

TABELAS_EM_ORDEM = ("itens_pedido", "pedidos", "produtos", "usuarios")


class AdminModel:
    def __init__(self, obter_conexao):
        self._conexao = obter_conexao

    def limpar_tabelas(self):
        conexao = self._conexao()
        with conexao:
            for tabela in TABELAS_EM_ORDEM:  # nomes fixos (lista branca), não vindos do cliente
                conexao.execute(f"DELETE FROM {tabela}")
