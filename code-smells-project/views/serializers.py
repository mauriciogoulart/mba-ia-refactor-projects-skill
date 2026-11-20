"""Serialização de saída por lista branca de campos (sem senha/hash nem configuração interna)."""

CAMPOS_PRODUTO = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")
CAMPOS_USUARIO = ("id", "nome", "email", "tipo", "criado_em")
CAMPOS_USUARIO_LOGIN = ("id", "nome", "email", "tipo")
CAMPOS_PEDIDO = ("id", "usuario_id", "status", "total", "criado_em")


def _selecionar(registro, campos):
    return {campo: registro[campo] for campo in campos}


def produto_publico(produto):
    return _selecionar(produto, CAMPOS_PRODUTO)


def usuario_publico(usuario):
    return _selecionar(usuario, CAMPOS_USUARIO)


def usuario_login(usuario, token):
    return {**_selecionar(usuario, CAMPOS_USUARIO_LOGIN), "token": token}


def pedido_publico(pedido):
    dados = _selecionar(pedido, CAMPOS_PEDIDO)
    dados["itens"] = [
        {
            "produto_id": item["produto_id"],
            "produto_nome": item["produto_nome"] if item["produto_nome"] is not None else "Desconhecido",
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
        }
        for item in pedido["itens"]
    ]
    return dados
