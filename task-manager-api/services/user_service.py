import logging

from models.constants import ROLE_USER
from models.task import Task
from models.user import User
from services.persistence import commit, remove, save
from utils.errors import AppError
from validators.user_validator import parse_role

logger = logging.getLogger(__name__)


def _is_admin(actor):
    return actor is not None and actor.is_admin()


def _ensure_email_available(email, user_id=None):
    existing = User.find_by_email(email)
    if existing and existing.id != user_id:
        raise AppError('Email já cadastrado', 409)


def list_users(limit, offset):
    """Devolve pares (usuário, quantidade de tasks)."""
    totals = Task.totals_by_user()
    return [(user, totals.get(user.id, (0, 0))[0]) for user in User.list_page(limit, offset)]


def get_user(user_id):
    user = User.find(user_id)
    if not user:
        raise AppError('Usuário não encontrado', 404)
    return user


def get_user_tasks(user_id):
    get_user(user_id)
    return Task.list_by_user(user_id)


def create_user(fields, actor):
    _ensure_email_available(fields['email'])
    role = parse_role(fields['role'])
    if role != ROLE_USER and not _is_admin(actor):
        raise AppError('Sem permissão', 403)

    user = User(name=fields['name'], email=fields['email'], role=role)
    user.set_password(fields['password'])
    save(user, 'Erro ao criar usuário')
    logger.info('Usuário criado user_id=%s', user.id)
    return user


def ensure_can_edit(user_id, actor):
    if actor.id != user_id and not actor.is_admin():
        raise AppError('Sem permissão', 403)


def update_user(user_id, fields, actor):
    user = get_user(user_id)
    if ('role' in fields or 'active' in fields) and not actor.is_admin():
        raise AppError('Sem permissão', 403)
    if 'email' in fields:
        _ensure_email_available(fields['email'], user_id)

    for name in ('name', 'email', 'role', 'active'):
        if name in fields:
            setattr(user, name, fields[name])
    if 'password' in fields:
        user.set_password(fields['password'])

    commit('Erro ao atualizar')
    logger.info('Usuário atualizado user_id=%s', user.id)
    return user


def delete_user(user_id):
    user = get_user(user_id)
    remove([*Task.list_by_user(user_id), user], 'Erro ao deletar')
    logger.info('Usuário deletado user_id=%s', user_id)
