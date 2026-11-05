"""Serialização de saída com lista branca de campos (nunca expõe senha/segredos)."""

_CAMPOS_PRODUTO = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")
_CAMPOS_USUARIO = ("id", "nome", "email", "tipo", "criado_em")
_CAMPOS_USUARIO_LOGIN = ("id", "nome", "email", "tipo")
_CAMPOS_PEDIDO = ("id", "usuario_id", "status", "total", "criado_em")
_CAMPOS_ITEM = ("produto_id", "produto_nome", "quantidade", "preco_unitario")


def _selecionar(origem, campos):
    return {campo: origem[campo] for campo in campos}


def produto(entidade):
    return _selecionar(entidade, _CAMPOS_PRODUTO)


def usuario(entidade):
    return _selecionar(entidade, _CAMPOS_USUARIO)


def usuario_login(entidade):
    return _selecionar(entidade, _CAMPOS_USUARIO_LOGIN)


def pedido(entidade):
    saida = _selecionar(entidade, _CAMPOS_PEDIDO)
    saida["itens"] = [_selecionar(item, _CAMPOS_ITEM) for item in entidade["itens"]]
    return saida
