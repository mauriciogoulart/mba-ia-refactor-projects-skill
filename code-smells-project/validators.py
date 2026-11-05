"""Validação de formato da entrada na borda (controllers). Lança AppError(400)."""
from constants import (
    CATEGORIA_PADRAO,
    CATEGORIAS_VALIDAS,
    NOME_PRODUTO_MAX,
    NOME_PRODUTO_MIN,
    STATUS_PEDIDO_VALIDOS,
)
from errors import AppError


def _eh_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _eh_inteiro(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def _exigir_objeto(dados):
    if not dados or not isinstance(dados, dict):
        raise AppError("Dados inválidos")


def validar_produto(dados):
    """Mesmas regras para criar e atualizar produto."""
    _exigir_objeto(dados)
    for campo, mensagem in (
        ("nome", "Nome é obrigatório"),
        ("preco", "Preço é obrigatório"),
        ("estoque", "Estoque é obrigatório"),
    ):
        if campo not in dados:
            raise AppError(mensagem)

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    if not isinstance(nome, str):
        raise AppError("Nome inválido")
    if not isinstance(descricao, str):
        raise AppError("Descrição inválida")
    if not _eh_numero(preco):
        raise AppError("Preço inválido")
    if not _eh_inteiro(estoque):
        raise AppError("Estoque inválido")

    if preco < 0:
        raise AppError("Preço não pode ser negativo")
    if estoque < 0:
        raise AppError("Estoque não pode ser negativo")
    if len(nome) < NOME_PRODUTO_MIN:
        raise AppError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_MAX:
        raise AppError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise AppError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def validar_filtros_busca(argumentos):
    termo = argumentos.get("q", "")
    categoria = argumentos.get("categoria", None)
    return termo, categoria, _ler_preco(argumentos, "preco_min"), _ler_preco(argumentos, "preco_max")


def _ler_preco(argumentos, nome):
    bruto = argumentos.get(nome, None)
    if bruto is None or bruto == "":
        return None
    try:
        return float(bruto)
    except ValueError:
        raise AppError(nome + " inválido")


def validar_novo_usuario(dados):
    _exigir_objeto(dados)
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not all(isinstance(valor, str) and valor for valor in (nome, email, senha)):
        raise AppError("Nome, email e senha são obrigatórios")
    return {"nome": nome, "email": email, "senha": senha}


def validar_login(dados):
    _exigir_objeto(dados)
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not all(isinstance(valor, str) and valor for valor in (email, senha)):
        raise AppError("Email e senha são obrigatórios")
    return {"email": email, "senha": senha}


def validar_novo_pedido(dados):
    _exigir_objeto(dados)
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise AppError("Usuario ID é obrigatório")
    if not itens:
        raise AppError("Pedido deve ter pelo menos 1 item")
    if not _eh_inteiro(usuario_id) or usuario_id < 1:
        raise AppError("Usuario ID inválido")
    if not isinstance(itens, list):
        raise AppError("Itens inválidos")

    itens_validos = []
    for item in itens:
        if not isinstance(item, dict):
            raise AppError("Item inválido")
        produto_id = item.get("produto_id")
        quantidade = item.get("quantidade")
        if not _eh_inteiro(produto_id) or produto_id < 1:
            raise AppError("Item inválido: produto_id deve ser inteiro positivo")
        if not _eh_inteiro(quantidade) or quantidade < 1:
            raise AppError("Item inválido: quantidade deve ser inteiro positivo")
        itens_validos.append({"produto_id": produto_id, "quantidade": quantidade})

    return {"usuario_id": usuario_id, "itens": itens_validos}


def validar_status_pedido(dados):
    _exigir_objeto(dados)
    status = dados.get("status", "")
    if not isinstance(status, str) or status not in STATUS_PEDIDO_VALIDOS:
        raise AppError("Status inválido")
    return status
