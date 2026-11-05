"""Operações de sistema: health check e reset administrativo."""
import logging

from models import sistema_model

logger = logging.getLogger(__name__)


class SistemaService:
    def __init__(self, obter_db):
        self._obter_db = obter_db

    def contagens(self):
        return sistema_model.contagens(self._obter_db())

    def resetar_banco(self):
        db = self._obter_db()
        try:
            sistema_model.apagar_tudo(db)
            db.commit()
        except Exception:
            db.rollback()
            raise
        logger.warning("Banco de dados resetado por administrador")
