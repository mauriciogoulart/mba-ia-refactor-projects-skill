import logging

from sqlalchemy.exc import SQLAlchemyError

from database import db
from services.exceptions import AppError

logger = logging.getLogger(__name__)


def commit(error_message):
    """Confirma a transação; em falha faz rollback e devolve 500 com a mensagem do contrato."""
    try:
        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        # Só o tipo da exceção: o texto do SQLAlchemy inclui parâmetros (dados pessoais).
        logger.error("Falha de persistência (%s): %s", type(exc).__name__, error_message)
        raise AppError(error_message, 500) from exc
