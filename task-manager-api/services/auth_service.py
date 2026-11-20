import logging

from models.user import User
from services.persistence import commit
from utils.errors import AppError

logger = logging.getLogger(__name__)


def authenticate(email, password, throttle, client_id):
    """Valida as credenciais respeitando o limite de falhas de login."""
    attempt_key = (client_id, email.lower())
    if throttle.is_blocked(attempt_key):
        logger.warning('Login bloqueado por excesso de falhas')
        raise AppError('Muitas tentativas de login. Tente novamente mais tarde', 429)

    user = User.find_by_email(email)
    stored_hash = user.password if user else None
    if not user or not user.check_password(password):
        throttle.register_failure(attempt_key)
        raise AppError('Credenciais inválidas', 401)

    throttle.reset(attempt_key)
    if user.password != stored_hash:
        commit('Erro ao atualizar credenciais')
        logger.info('Hash de senha legado migrado user_id=%s', user.id)

    if not user.active:
        raise AppError('Usuário inativo', 403)
    return user


def find_active_user(user_id):
    user = User.find(user_id)
    return user if user and user.active else None
