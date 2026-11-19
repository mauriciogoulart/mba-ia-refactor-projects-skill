import hashlib
import hmac

from itsdangerous import BadSignature, URLSafeTimedSerializer


class TokenService:
    """Emite e verifica tokens de acesso assinados, com validade e vinculados à credencial da conta."""

    def __init__(self, secret_key, max_age_seconds):
        self._secret_key = secret_key.encode()
        self._serializer = URLSafeTimedSerializer(secret_key, salt='auth-token')
        self._max_age_seconds = max_age_seconds

    def _fingerprint(self, password_hash):
        """Impressão do hash de senha atual (HMAC truncado); o hash nunca vai para o token."""
        return hmac.new(self._secret_key, password_hash.encode(), hashlib.sha256).hexdigest()[:32]

    def issue(self, user):
        return self._serializer.dumps({'user_id': user.id, 'fp': self._fingerprint(user.password)})

    def verify(self, token, load_user):
        """Devolve o usuário do token, ou None se o token for inválido, expirado ou de outra credencial.

        A impressão invalida o token quando a senha muda ou quando o id passa a pertencer a outra conta.
        """
        try:
            payload = self._serializer.loads(token, max_age=self._max_age_seconds)
        except BadSignature:
            return None
        if not isinstance(payload, dict):
            return None
        user_id, fingerprint = payload.get('user_id'), payload.get('fp')
        if not isinstance(user_id, int) or isinstance(user_id, bool) or not isinstance(fingerprint, str):
            return None
        user = load_user(user_id)
        if user is None or not hmac.compare_digest(fingerprint.encode(), self._fingerprint(user.password).encode()):
            return None
        return user
