from flask_sqlalchemy import SQLAlchemy

from utils.limits import MAX_SQL_INTEGER

db = SQLAlchemy()


def get_by_id(model, entity_id):
    """Busca por chave primária; ids fora da faixa do banco não existem."""
    if abs(entity_id) > MAX_SQL_INTEGER:
        return None
    return db.session.get(model, entity_id)
