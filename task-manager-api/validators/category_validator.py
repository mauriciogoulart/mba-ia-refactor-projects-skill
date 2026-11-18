import re

from models.constants import DEFAULT_COLOR
from utils.errors import AppError
from validators.common import require_object

FORMATO_COR = re.compile(r'#[0-9a-fA-F]{6}')


def _parse_name(value):
    if not isinstance(value, str) or not value.strip():
        raise AppError('Nome inválido')
    return value


def _parse_description(value):
    if value is not None and not isinstance(value, str):
        raise AppError('Descrição inválida')
    return value


def _parse_color(value):
    if not isinstance(value, str) or not FORMATO_COR.fullmatch(value):
        raise AppError('Cor inválida. Use #RRGGBB')
    return value


def parse_new_category(data):
    require_object(data)
    if not data.get('name'):
        raise AppError('Nome é obrigatório')
    return {
        'name': _parse_name(data['name']),
        'description': _parse_description(data.get('description', '')),
        'color': _parse_color(data.get('color', DEFAULT_COLOR)),
    }


def parse_category_update(data):
    if not isinstance(data, dict):
        raise AppError('Dados inválidos')
    fields = {}
    if 'name' in data:
        fields['name'] = _parse_name(data['name'])
    if 'description' in data:
        fields['description'] = _parse_description(data['description'])
    if 'color' in data:
        fields['color'] = _parse_color(data['color'])
    return fields
