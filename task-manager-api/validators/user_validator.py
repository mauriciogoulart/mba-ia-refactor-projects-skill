import re

from models.constants import MIN_PASSWORD_LENGTH, ROLE_USER, VALID_ROLES
from utils.errors import AppError
from validators.common import require_object

FORMATO_EMAIL = re.compile(r'[a-zA-Z0-9+_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+')


def _parse_name(value):
    if not isinstance(value, str) or not value.strip():
        raise AppError('Nome inválido')
    return value


def _parse_email(value):
    if not isinstance(value, str) or not FORMATO_EMAIL.fullmatch(value):
        raise AppError('Email inválido')
    return value


def parse_role(value):
    if value not in VALID_ROLES:
        raise AppError('Role inválido')
    return value


def parse_new_user(data):
    require_object(data)
    if not data.get('name'):
        raise AppError('Nome é obrigatório')
    if not data.get('email'):
        raise AppError('Email é obrigatório')
    if not data.get('password'):
        raise AppError('Senha é obrigatória')

    password = data['password']
    fields = {'name': _parse_name(data['name']), 'email': _parse_email(data['email'])}
    if not isinstance(password, str):
        raise AppError('Senha inválida')
    if len(password) < MIN_PASSWORD_LENGTH:
        raise AppError(f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres')
    return {**fields, 'password': password, 'role': data.get('role', ROLE_USER)}


def parse_user_update(data):
    require_object(data)
    fields = {}
    if 'name' in data:
        fields['name'] = _parse_name(data['name'])
    if 'email' in data:
        fields['email'] = _parse_email(data['email'])
    if 'password' in data:
        password = data['password']
        if not isinstance(password, str):
            raise AppError('Senha inválida')
        if len(password) < MIN_PASSWORD_LENGTH:
            raise AppError('Senha muito curta')
        fields['password'] = password
    if 'role' in data:
        fields['role'] = parse_role(data['role'])
    if 'active' in data:
        if not isinstance(data['active'], bool):
            raise AppError('Campo active inválido')
        fields['active'] = data['active']
    return fields


def parse_credentials(data):
    require_object(data)
    email = data.get('email')
    password = data.get('password')
    if not email or not password or not isinstance(email, str) or not isinstance(password, str):
        raise AppError('Email e senha são obrigatórios')
    return email, password
