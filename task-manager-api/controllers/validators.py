"""Validação de entrada na borda (formato, tipo e faixa); mensagens do contrato original."""
import re
from datetime import datetime

from services.exceptions import AppError
from utils.constants import (DATE_FORMAT, DEFAULT_COLOR, DEFAULT_PRIORITY, DEFAULT_STATUS,
                             MAX_PRIORITY, MAX_TITLE_LENGTH, MIN_PASSWORD_LENGTH, MIN_PRIORITY,
                             MIN_TITLE_LENGTH, ROLE_USER, VALID_ROLES, VALID_STATUSES)
from utils.helpers import is_valid_color

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+$')
INVALID_DATA = 'Dados inválidos'


def require_object(data, allow_empty=False):
    if not isinstance(data, dict) or (not data and not allow_empty):
        raise AppError(INVALID_DATA)
    return data


def _is_number(value):
    return isinstance(value, (int, float))


# ---------- tasks ----------

def _check_title(title):
    if not isinstance(title, str):
        raise AppError('Título inválido')
    if len(title) < MIN_TITLE_LENGTH:
        raise AppError('Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise AppError('Título muito longo')


def _check_status(status):
    if status not in VALID_STATUSES:
        raise AppError('Status inválido')


def _check_priority(priority):
    if not _is_number(priority):
        raise AppError('Prioridade inválida')
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise AppError('Prioridade deve ser entre 1 e 5')


def _check_reference(value):
    if value and not isinstance(value, (int, float, str)):
        raise AppError(INVALID_DATA)
    return value


def _parse_due_date(value, message):
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except (TypeError, ValueError):
        raise AppError(message)


def _parse_tags(tags):
    if isinstance(tags, list):
        if not all(isinstance(tag, str) for tag in tags):
            raise AppError('Tags inválidas')
        return ','.join(tags)
    if isinstance(tags, str):
        return tags
    if tags:
        raise AppError('Tags inválidas')
    return None


def parse_task_create(data):
    data = require_object(data)
    title = data.get('title')
    if not title:
        raise AppError('Título é obrigatório')
    _check_title(title)

    status = data.get('status', DEFAULT_STATUS)
    _check_status(status)
    priority = data.get('priority', DEFAULT_PRIORITY)
    _check_priority(priority)

    fields = {
        'title': title,
        'description': data.get('description', ''),
        'status': status,
        'priority': priority,
        'user_id': _check_reference(data.get('user_id')),
        'category_id': _check_reference(data.get('category_id')),
    }
    if data.get('due_date'):
        fields['due_date'] = _parse_due_date(data['due_date'], 'Formato de data inválido. Use YYYY-MM-DD')
    if data.get('tags'):
        fields['tags'] = _parse_tags(data['tags'])
    return fields


def parse_task_update(data):
    data = require_object(data)
    fields = {}
    if 'title' in data:
        _check_title(data['title'])
        fields['title'] = data['title']
    if 'description' in data:
        fields['description'] = data['description']
    if 'status' in data:
        _check_status(data['status'])
        fields['status'] = data['status']
    if 'priority' in data:
        _check_priority(data['priority'])
        fields['priority'] = data['priority']
    if 'user_id' in data:
        fields['user_id'] = _check_reference(data['user_id'])
    if 'category_id' in data:
        fields['category_id'] = _check_reference(data['category_id'])
    if 'due_date' in data:
        due_date = data['due_date']
        fields['due_date'] = _parse_due_date(due_date, 'Formato de data inválido') if due_date else None
    if 'tags' in data:
        fields['tags'] = _parse_tags(data['tags'])
    return fields


def parse_search_args(args):
    def as_int(name):
        value = args.get(name, '')
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            raise AppError(f'Parâmetro {name} inválido')

    return {
        'text': args.get('q', ''),
        'status': args.get('status', ''),
        'priority': as_int('priority'),
        'user_id': as_int('user_id'),
    }


# ---------- usuários ----------

def _check_name(name):
    if not isinstance(name, str) or not name.strip():
        raise AppError('Nome inválido')


def _check_email(email):
    if not isinstance(email, str) or not EMAIL_PATTERN.match(email):
        raise AppError('Email inválido')


def _check_role(role):
    if role not in VALID_ROLES:
        raise AppError('Role inválido')


def parse_user_create(data):
    data = require_object(data)
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', ROLE_USER)

    if not name:
        raise AppError('Nome é obrigatório')
    if not email:
        raise AppError('Email é obrigatório')
    if not password:
        raise AppError('Senha é obrigatória')
    _check_name(name)
    _check_email(email)
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise AppError('Senha deve ter no mínimo 4 caracteres')
    _check_role(role)
    return {'name': name, 'email': email, 'password': password, 'role': role}


def parse_user_update(data):
    data = require_object(data)
    fields = {}
    if 'name' in data:
        _check_name(data['name'])
        fields['name'] = data['name']
    if 'email' in data:
        _check_email(data['email'])
        fields['email'] = data['email']
    if 'password' in data:
        password = data['password']
        if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
            raise AppError('Senha muito curta')
        fields['password'] = password
    if 'role' in data:
        _check_role(data['role'])
        fields['role'] = data['role']
    if 'active' in data:
        if not isinstance(data['active'], bool):
            raise AppError('Campo active inválido')
        fields['active'] = data['active']
    return fields


def parse_login(data):
    data = require_object(data)
    email = data.get('email')
    password = data.get('password')
    if not email or not password or not isinstance(email, str) or not isinstance(password, str):
        raise AppError('Email e senha são obrigatórios')
    return email, password


# ---------- categorias ----------

def _check_color(color):
    if not is_valid_color(color):
        raise AppError('Cor inválida')


def parse_category_create(data):
    data = require_object(data)
    name = data.get('name')
    if not name:
        raise AppError('Nome é obrigatório')
    _check_name(name)
    color = data.get('color', DEFAULT_COLOR)
    _check_color(color)
    return {'name': name, 'description': data.get('description', ''), 'color': color}


def parse_category_update(data):
    data = require_object(data, allow_empty=True)
    fields = {}
    if 'name' in data:
        _check_name(data['name'])
        fields['name'] = data['name']
    if 'description' in data:
        fields['description'] = data['description']
    if 'color' in data:
        _check_color(data['color'])
        fields['color'] = data['color']
    return fields
