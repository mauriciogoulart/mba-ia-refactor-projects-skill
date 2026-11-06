import logging

from itsdangerous import BadSignature, URLSafeTimedSerializer

from models.user import User
from services.exceptions import AppError
from services.persistence import commit

logger = logging.getLogger(__name__)

INVALID_CREDENTIALS = 'Credenciais inválidas'


class TokenSigner:
    """Emite e verifica tokens assinados com a SECRET_KEY e prazo de validade."""

    def __init__(self, secret_key, max_age):
        self._serializer = URLSafeTimedSerializer(secret_key, salt='auth-token')
        self._max_age = max_age

    def issue(self, user):
        return self._serializer.dumps({'uid': user.id})

    def user_id_from(self, token):
        try:
            payload = self._serializer.loads(token, max_age=self._max_age)
        except BadSignature:
            return None
        return payload.get('uid') if isinstance(payload, dict) else None


def authenticate(email, password):
    user = User.find_by_email(email)
    if not user or not user.check_password(password):
        raise AppError(INVALID_CREDENTIALS, 401)
    if not user.active:
        raise AppError('Usuário inativo', 403)
    if user.password_needs_rehash():
        user.set_password(password)
        commit('Erro interno')
        logger.info("Hash de senha legado migrado: user_id=%s", user.id)
    return user


def active_user_from_token(signer, token):
    user_id = signer.user_id_from(token) if token else None
    user = User.get(user_id) if user_id else None
    return user if user and user.active else None
