from itsdangerous import BadSignature, URLSafeTimedSerializer


class TokenService:
    """Emite e verifica tokens de acesso assinados e com validade."""

    def __init__(self, secret_key, max_age_seconds):
        self._serializer = URLSafeTimedSerializer(secret_key, salt='auth-token')
        self._max_age_seconds = max_age_seconds

    def issue(self, user_id):
        return self._serializer.dumps({'user_id': user_id})

    def verify(self, token):
        """Devolve o id do usuário ou None se o token for inválido ou estiver expirado."""
        try:
            payload = self._serializer.loads(token, max_age=self._max_age_seconds)
        except BadSignature:
            return None
        return payload.get('user_id') if isinstance(payload, dict) else None
