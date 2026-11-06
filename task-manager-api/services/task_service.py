import logging

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from services.exceptions import AppError
from services.persistence import commit
from utils.constants import VALID_STATUSES, STATUS_DONE
from utils.helpers import calculate_percentage, utc_now

logger = logging.getLogger(__name__)

TASK_NOT_FOUND = 'Task não encontrada'


def get_task(task_id):
    task = Task.get(task_id)
    if not task:
        raise AppError(TASK_NOT_FOUND, 404)
    return task


def _ensure_reference(model, ref_id, message):
    if ref_id and not model.get(ref_id):
        raise AppError(message, 404)


def _ensure_references(fields):
    if 'user_id' in fields:
        _ensure_reference(User, fields['user_id'], 'Usuário não encontrado')
    if 'category_id' in fields:
        _ensure_reference(Category, fields['category_id'], 'Categoria não encontrada')


def list_tasks():
    return Task.list_with_relations()


def create_task(fields):
    _ensure_references(fields)
    task = Task(**fields)
    db.session.add(task)
    commit('Erro ao criar task')
    logger.info("Task criada: id=%s", task.id)
    return task


def update_task(task_id, fields):
    task = get_task(task_id)
    _ensure_references(fields)
    for name, value in fields.items():
        setattr(task, name, value)
    task.updated_at = utc_now()
    commit('Erro ao atualizar')
    logger.info("Task atualizada: id=%s", task.id)
    return task


def delete_task(task_id):
    task = get_task(task_id)
    db.session.delete(task)
    commit('Erro ao deletar')
    logger.info("Task deletada: id=%s", task_id)


def search_tasks(text, status, priority, user_id):
    return Task.search(text=text, status=status, priority=priority, user_id=user_id)


def task_stats():
    total = Task.count_all()
    by_status = Task.count_by_status()
    stats = {status: by_status.get(status, 0) for status in VALID_STATUSES}
    stats['total'] = total
    stats['overdue'] = Task.count_overdue(utc_now())
    stats['completion_rate'] = calculate_percentage(by_status.get(STATUS_DONE, 0), total)
    return stats
