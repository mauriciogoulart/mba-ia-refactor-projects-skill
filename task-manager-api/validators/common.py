from models.constants import MAX_PAGE_SIZE
from utils.errors import AppError
from utils.limits import MAX_SQL_INTEGER


def require_object(data):
    if not data or not isinstance(data, dict):
        raise AppError('Dados inválidos')
    return data


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
