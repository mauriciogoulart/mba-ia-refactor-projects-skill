from datetime import datetime

from models.constants import (
    DEFAULT_PRIORITY,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    STATUS_PENDING,
    VALID_STATUSES,
)
from utils.errors import AppError
from utils.limits import MAX_SQL_INTEGER
from validators.common import parse_int_param, require_object

FORMATO_DATA = '%Y-%m-%d'


def _parse_title(value):
    if not isinstance(value, str):
        raise AppError('Título inválido')
    if len(value) < MIN_TITLE_LENGTH:
        raise AppError('Título muito curto')
    if len(value) > MAX_TITLE_LENGTH:
        raise AppError('Título muito longo')
    return value


def _parse_description(value):
    if value is not None and not isinstance(value, str):
        raise AppError('Descrição inválida')
    return value


def _parse_status(value):
    if value not in VALID_STATUSES:
        raise AppError('Status inválido')
    return value


def _parse_priority(value):
    if not isinstance(value, (int, float)) or not MIN_PRIORITY <= value <= MAX_PRIORITY:
        raise AppError(f'Prioridade deve ser entre {MIN_PRIORITY} e {MAX_PRIORITY}')
    return value


def _parse_reference(value, invalid_message, not_found_message):
    """Normaliza o id de uma referência; texto não numérico equivale a registro inexistente."""
    if value is None or value == '':
        return None
    if isinstance(value, str):
        try:
            value = int(value)
        except ValueError as exc:
            raise AppError(not_found_message, 404) from exc
    if isinstance(value, bool) or not isinstance(value, int) or abs(value) > MAX_SQL_INTEGER:
        raise AppError(invalid_message)
    return value


def _parse_user_reference(value):
    return _parse_reference(value, 'Usuário inválido', 'Usuário não encontrado')


def _parse_category_reference(value):
    return _parse_reference(value, 'Categoria inválida', 'Categoria não encontrada')


def _parse_due_date(value, message):
    try:
        return datetime.strptime(value, FORMATO_DATA)
    except (TypeError, ValueError) as exc:
        raise AppError(message) from exc


def _parse_tags(value):
    if isinstance(value, list):
        if not all(isinstance(tag, str) for tag in value):
            raise AppError('Tags inválidas')
        return ','.join(value)
    if value is not None and not isinstance(value, str):
        raise AppError('Tags inválidas')
    return value


def parse_new_task(data):
    require_object(data)
    if not data.get('title'):
        raise AppError('Título é obrigatório')

    due_date = data.get('due_date')
    tags = data.get('tags')
    return {
        'title': _parse_title(data['title']),
        'description': _parse_description(data.get('description', '')),
        'status': _parse_status(data.get('status', STATUS_PENDING)),
        'priority': _parse_priority(data.get('priority', DEFAULT_PRIORITY)),
        'user_id': _parse_user_reference(data.get('user_id')),
        'category_id': _parse_category_reference(data.get('category_id')),
        'due_date': _parse_due_date(due_date, 'Formato de data inválido. Use YYYY-MM-DD') if due_date else None,
        'tags': _parse_tags(tags) if tags else None,
    }


def parse_task_update(data):
    require_object(data)
    fields = {}
    if 'title' in data:
        fields['title'] = _parse_title(data['title'])
    if 'description' in data:
        fields['description'] = _parse_description(data['description'])
    if 'status' in data:
        fields['status'] = _parse_status(data['status'])
    if 'priority' in data:
        fields['priority'] = _parse_priority(data['priority'])
    if 'user_id' in data:
        fields['user_id'] = _parse_user_reference(data['user_id'])
    if 'category_id' in data:
        fields['category_id'] = _parse_category_reference(data['category_id'])
    if 'due_date' in data:
        due_date = data['due_date']
        fields['due_date'] = _parse_due_date(due_date, 'Formato de data inválido') if due_date else None
    if 'tags' in data:
        fields['tags'] = _parse_tags(data['tags'])
    return fields


def parse_search_filters(args):
    priority = args.get('priority', '')
    user_id = args.get('user_id', '')
    return {
        'term': args.get('q', ''),
        'status': args.get('status', ''),
        'priority': parse_int_param(priority, 'Prioridade inválida') if priority else None,
        'user_id': parse_int_param(user_id, 'Usuário inválido') if user_id else None,
    }
