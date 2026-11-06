import logging

from database import db
from models.task import Task
from models.user import User
from services.exceptions import AppError
from services.persistence import commit

logger = logging.getLogger(__name__)

USER_NOT_FOUND = 'Usuário não encontrado'
EMAIL_TAKEN = 'Email já cadastrado'


def get_user(user_id):
    user = User.get(user_id)
    if not user:
        raise AppError(USER_NOT_FOUND, 404)
    return user


def list_users_with_task_count():
    counts = Task.count_by_user()
    return [(user, counts.get(user.id, 0)) for user in User.list_all()]


def get_user_with_tasks(user_id):
    user = get_user(user_id)
    return user, Task.list_by_user(user_id)


def list_user_tasks(user_id):
    get_user(user_id)
    return Task.list_by_user(user_id)


def create_user(fields):
    if User.find_by_email(fields['email']):
        raise AppError(EMAIL_TAKEN, 409)
    user = User(name=fields['name'], email=fields['email'], role=fields['role'])
    user.set_password(fields['password'])
    db.session.add(user)
    commit('Erro ao criar usuário')
    logger.info("Usuário criado: id=%s", user.id)
    return user


def update_user(user, fields):
    if 'email' in fields:
        existing = User.find_by_email(fields['email'])
        if existing and existing.id != user.id:
            raise AppError(EMAIL_TAKEN, 409)
    for name, value in fields.items():
        if name == 'password':
            user.set_password(value)
        else:
            setattr(user, name, value)
    commit('Erro ao atualizar')
    return user


def delete_user(user_id):
    user = get_user(user_id)
    for task in Task.list_by_user(user_id):
        db.session.delete(task)
    db.session.delete(user)
    commit('Erro ao deletar')
    logger.info("Usuário deletado: id=%s", user_id)
