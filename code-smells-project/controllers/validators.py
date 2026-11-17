"""Validação de formato das entradas (na borda, antes de qualquer efeito)."""
from services.erros import AppError
from services.regras import (CATEGORIA_PADRAO, CATEGORIAS_VALIDAS, NOME_PRODUTO_MAX, NOME_PRODUTO_MIN,
                             STATUS_PEDIDO)

LIMITE_MAXIMO_PAGINA = 1000


def _numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _inteiro_positivo(valor):
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


def _texto_preenchido(valor):
    return isinstance(valor, str) and valor != ""


def validar_produto(dados):
    if not isinstance(dados, dict) or not dados:
        raise AppError("Dados inválidos")
    for campo, mensagem in (("nome", "Nome é obrigatório"), ("preco", "Preço é obrigatório"),
                            ("estoque", "Estoque é obrigatório")):
        if campo not in dados:
            raise AppError(mensagem)
    nome, preco, estoque = dados["nome"], dados["preco"], dados["estoque"]
    descricao = dados.get("descricao", "")
    categoria = dados.get("categoria", CATEGORIA_PADRAO)
    if not isinstance(nome, str):
        raise AppError("Nome inválido")
    if not _numero(preco):
        raise AppError("Preço inválido")
    if not _numero(estoque) or float(estoque) != int(estoque):
        raise AppError("Estoque inválido")
    if not isinstance(descricao, str):
        raise AppError("Descrição inválida")
    if preco < 0:
        raise AppError("Preço não pode ser negativo")
    if estoque < 0:
        raise AppError("Estoque não pode ser negativo")
    if len(nome) < NOME_PRODUTO_MIN:
        raise AppError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_MAX:
        raise AppError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise AppError(f"Categoria inválida. Válidas: {list(CATEGORIAS_VALIDAS)}")
    return {"nome": nome, "descricao": descricao, "preco": preco, "estoque": int(estoque), "categoria": categoria}


def validar_busca(args):
    def _preco(nome):
        valor = args.get(nome)
        if not valor:
            return None
        try:
            return float(valor)
        except ValueError:
            raise AppError(f"{nome} inválido") from None

    return {"termo": args.get("q", ""), "categoria": args.get("categoria") or None,
            "preco_min": _preco("preco_min"), "preco_max": _preco("preco_max")}


def validar_paginacao(args):
    """Parâmetros opcionais `limite`/`offset`; sem eles a listagem é completa (comportamento original)."""
    if "limite" not in args and "offset" not in args:
        return None, 0
    try:
        limite = int(args.get("limite", LIMITE_MAXIMO_PAGINA))
        offset = int(args.get("offset", 0))
    except ValueError:
        raise AppError("Paginação inválida") from None
    if not 1 <= limite <= LIMITE_MAXIMO_PAGINA or offset < 0:
        raise AppError("Paginação inválida")
    return limite, offset


def validar_usuario(dados):
    if not isinstance(dados, dict) or not dados:
        raise AppError("Dados inválidos")
    nome, email, senha = dados.get("nome", ""), dados.get("email", ""), dados.get("senha", "")
    if not (_texto_preenchido(nome) and _texto_preenchido(email) and _texto_preenchido(senha)):
        raise AppError("Nome, email e senha são obrigatórios")
    return {"nome": nome, "email": email, "senha": senha}


def validar_login(dados):
    dados = dados if isinstance(dados, dict) else {}
    email, senha = dados.get("email", ""), dados.get("senha", "")
    if not (_texto_preenchido(email) and _texto_preenchido(senha)):
        raise AppError("Email e senha são obrigatórios")
    return email, senha


def validar_pedido(dados):
    if not isinstance(dados, dict) or not dados:
        raise AppError("Dados inválidos")
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        raise AppError("Usuario ID é obrigatório")
    if not _inteiro_positivo(usuario_id):
        raise AppError("Usuario ID inválido")
    if not isinstance(itens, list) or not itens:
        raise AppError("Pedido deve ter pelo menos 1 item")
    normalizados = []
    for item in itens:
        if not (isinstance(item, dict) and _inteiro_positivo(item.get("produto_id"))
                and _inteiro_positivo(item.get("quantidade"))):
            raise AppError("Item inválido: produto_id e quantidade devem ser inteiros positivos")
        normalizados.append({"produto_id": item["produto_id"], "quantidade": item["quantidade"]})
    return usuario_id, normalizados


def validar_status(dados):
    status = dados.get("status", "") if isinstance(dados, dict) else ""
    if status not in STATUS_PEDIDO:
        raise AppError("Status inválido")
    return status
