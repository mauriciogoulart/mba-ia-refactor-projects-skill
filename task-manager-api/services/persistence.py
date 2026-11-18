"""Fronteira transacional dos services: confirma ou desfaz a sessão atual."""
import logging

from sqlalchemy.exc import SQLAlchemyError

from database import db
from utils.errors import AppError

logger = logging.getLogger(__name__)


def commit(error_message):
    try:
        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        logger.exception('Falha ao confirmar a transação')
        raise AppError(error_message, 500) from exc


def save(entity, error_message):
    db.session.add(entity)
    commit(error_message)


def remove(entities, error_message):
    for entity in entities:
        db.session.delete(entity)
    commit(error_message)
