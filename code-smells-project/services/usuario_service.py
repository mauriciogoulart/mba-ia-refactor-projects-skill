"""Regras de negócio de usuários e autenticação."""
import hmac
import logging
import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from config.logging_config import mascarar
from constants import TIPO_CLIENTE
from errors import AppError
from models import usuario_model

logger = logging.getLogger(__name__)

_PREFIXOS_HASH = ("scrypt:", "pbkdf2:")


def _eh_hash(valor):
    return isinstance(valor, str) and valor.startswith(_PREFIXOS_HASH)


class UsuarioService:
    def __init__(self, obter_db):
        self._obter_db = obter_db

    def listar(self):
        return usuario_model.listar(self._obter_db())

    def obter(self, usuario_id):
        usuario = usuario_model.obter(self._obter_db(), usuario_id)
        if usuario is None:
            raise AppError("Usuário não encontrado", 404)
        return usuario

    def existe(self, usuario_id):
        return usuario_model.obter(self._obter_db(), usuario_id) is not None

    def criar(self, dados):
        db = self._obter_db()
        if usuario_model.obter_por_email(db, dados["email"]) is not None:
            raise AppError("Email já cadastrado", 409)
        try:
            usuario_id = usuario_model.criar(
                db, dados["nome"], dados["email"], generate_password_hash(dados["senha"]), TIPO_CLIENTE
            )
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            raise AppError("Email já cadastrado", 409)
        logger.info("Usuário criado id=%s", usuario_id)
        return usuario_id

    def autenticar(self, email, senha):
        db = self._obter_db()
        usuario = usuario_model.obter_por_email(db, email)
        if usuario is None or not self._senha_confere(db, usuario, senha):
            logger.warning("Login falhou email=%s", mascarar(email))
            raise AppError("Email ou senha inválidos", 401)
        logger.info("Login bem-sucedido usuario_id=%s", usuario["id"])
        return usuario

    def _senha_confere(self, db, usuario, senha):
        armazenada = usuario["senha"]
        if _eh_hash(armazenada):
            return check_password_hash(armazenada, senha)
        # Legado: senha em texto puro. Se conferir, regrava como hash (migração no login).
        if hmac.compare_digest(str(armazenada).encode(), senha.encode()):
            usuario_model.atualizar_senha(db, usuario["id"], generate_password_hash(senha))
            db.commit()
            logger.info("Senha migrada para hash usuario_id=%s", usuario["id"])
            return True
        return False
