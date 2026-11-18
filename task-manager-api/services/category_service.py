import logging

from models.category import Category
from models.task import Task
from services.persistence import commit, remove, save
from utils.errors import AppError

logger = logging.getLogger(__name__)


def list_categories(limit, offset):
    """Devolve pares (categoria, quantidade de tasks)."""
    totals = Task.count_by_category()
    return [(category, totals.get(category.id, 0)) for category in Category.list_page(limit, offset)]


def ensure_exists(category_id):
    category = Category.find(category_id)
    if not category:
        raise AppError('Categoria não encontrada', 404)
    return category


def create_category(fields):
    category = Category(**fields)
    save(category, 'Erro ao criar categoria')
    logger.info('Categoria criada category_id=%s', category.id)
    return category


def update_category(category_id, fields):
    category = ensure_exists(category_id)
    for name, value in fields.items():
        setattr(category, name, value)
    commit('Erro ao atualizar')
    return category


def delete_category(category_id):
    category = ensure_exists(category_id)
    # As tasks vinculadas são preservadas e ficam sem categoria na mesma transação.
    for task in category.tasks:
        task.category_id = None
    remove([category], 'Erro ao deletar')
    logger.info('Categoria deletada category_id=%s', category_id)
