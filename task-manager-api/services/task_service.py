import logging

from models.category import Category
from models.constants import STATUS_CANCELLED, STATUS_DONE, STATUS_IN_PROGRESS, STATUS_PENDING
from models.task import Task
from models.user import User
from services.persistence import commit, remove, save
from utils.clock import utcnow
from utils.errors import AppError

logger = logging.getLogger(__name__)


def completion_rate(completed, total):
    return round((completed / total) * 100, 2) if total > 0 else 0


def _ensure_references(fields):
    if fields.get('user_id') and User.find(fields['user_id']) is None:
        raise AppError('Usuário não encontrado', 404)
    if fields.get('category_id') and Category.find(fields['category_id']) is None:
        raise AppError('Categoria não encontrada', 404)


def _ensure_can_assign(assignee_id, actor):
    """Somente a gestão atribui tasks a terceiros ou as deixa sem responsável."""
    if assignee_id != actor.id and not actor.is_staff():
        raise AppError('Sem permissão', 403)


def list_tasks(limit, offset, actor):
    return Task.list_page(limit, offset, owner_id=actor.task_scope())


def search_tasks(filters, limit, offset, actor):
    return Task.search(limit=limit, offset=offset, owner_id=actor.task_scope(), **filters)


def _find_task(task_id):
    task = Task.find(task_id)
    if not task:
        raise AppError('Task não encontrada', 404)
    return task


def get_accessible_task(task_id, actor):
    """Devolve a task se o chamador for o responsável por ela ou tiver perfil de gestão."""
    task = _find_task(task_id)
    if task.user_id != actor.id and not actor.is_staff():
        raise AppError('Sem permissão', 403)
    return task


def create_task(fields, actor):
    if not actor.is_staff():
        _ensure_can_assign(fields['user_id'] or actor.id, actor)
        fields = {**fields, 'user_id': actor.id}
    _ensure_references(fields)
    task = Task(**fields)
    save(task, 'Erro ao criar task')
    logger.info('Task criada task_id=%s', task.id)
    return task


def update_task(task, fields, actor):
    if 'user_id' in fields:
        _ensure_can_assign(fields['user_id'], actor)
    _ensure_references(fields)
    for name, value in fields.items():
        setattr(task, name, value)
    task.updated_at = utcnow()
    commit('Erro ao atualizar')
    logger.info('Task atualizada task_id=%s', task.id)
    return task


def delete_task(task):
    task_id = task.id
    remove([task], 'Erro ao deletar')
    logger.info('Task deletada task_id=%s', task_id)


def get_stats(owner_id=None):
    total = Task.count_all(owner_id)
    by_status = Task.count_by_status(owner_id)
    done = by_status.get(STATUS_DONE, 0)
    return {
        'total': total,
        'pending': by_status.get(STATUS_PENDING, 0),
        'in_progress': by_status.get(STATUS_IN_PROGRESS, 0),
        'done': done,
        'cancelled': by_status.get(STATUS_CANCELLED, 0),
        'overdue': len(Task.list_overdue(owner_id)),
        'completion_rate': completion_rate(done, total),
    }
