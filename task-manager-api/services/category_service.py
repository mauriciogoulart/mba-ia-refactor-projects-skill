from database import db
from models.category import Category
from models.task import Task
from services.exceptions import AppError
from services.persistence import commit

CATEGORY_NOT_FOUND = 'Categoria não encontrada'


def get_category(category_id):
    category = Category.get(category_id)
    if not category:
        raise AppError(CATEGORY_NOT_FOUND, 404)
    return category


def list_categories_with_task_count():
    counts = Task.count_by_category()
    return [(category, counts.get(category.id, 0)) for category in Category.list_all()]


def create_category(fields):
    category = Category(**fields)
    db.session.add(category)
    commit('Erro ao criar categoria')
    return category


def update_category(category_id, fields):
    category = get_category(category_id)
    for name, value in fields.items():
        setattr(category, name, value)
    commit('Erro ao atualizar')
    return category


def delete_category(category_id):
    category = get_category(category_id)
    # SQLite não aplica FK por padrão: desvincula as tasks para não deixar referências órfãs.
    Task.detach_category(category_id)
    db.session.delete(category)
    commit('Erro ao deletar')
