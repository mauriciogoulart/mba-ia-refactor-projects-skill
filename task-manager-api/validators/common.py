from models.constants import MAX_PAGE_SIZE
from utils.errors import AppError
from utils.limits import MAX_SQL_INTEGER


def ensure_valid_text(data):
    """Rejeita textos que não podem ser gravados em UTF-8 (ex.: surrogate isolado), em qualquer nível."""
    pendentes = [data]
    while pendentes:
        valor = pendentes.pop()
        if isinstance(valor, str):
            try:
                valor.encode('utf-8')
            except UnicodeEncodeError as exc:
                raise AppError('Texto inválido') from exc
        elif isinstance(valor, dict):
            pendentes.extend(valor.keys())
            pendentes.extend(valor.values())
        elif isinstance(valor, list):
            pendentes.extend(valor)
    return data


def require_object(data):
    if not data or not isinstance(data, dict):
        raise AppError('Dados inválidos')
    return ensure_valid_text(data)


def parse_int_param(raw, message):
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise AppError(message) from exc
    if abs(value) > MAX_SQL_INTEGER:
        raise AppError(message)
    return value


def parse_pagination(args):
    limit = parse_int_param(args.get('limit', MAX_PAGE_SIZE), 'Parâmetro limit inválido')
    offset = parse_int_param(args.get('offset', 0), 'Parâmetro offset inválido')
    if limit < 1 or limit > MAX_PAGE_SIZE:
        raise AppError(f'Parâmetro limit deve ser entre 1 e {MAX_PAGE_SIZE}')
    if offset < 0:
        raise AppError('Parâmetro offset inválido')
    return limit, offset
