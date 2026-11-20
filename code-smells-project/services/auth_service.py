"""Emissão e verificação de token assinado (itsdangerous, chave da configuração)."""
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


class TokenService:
    def __init__(self, secret_key, max_age):
        self._serializer = URLSafeTimedSerializer(secret_key, salt="loja-auth-token")
        self._max_age = max_age

    def emitir(self, usuario):
        return self._serializer.dumps({"id": usuario["id"], "tipo": usuario["tipo"]})

    def verificar(self, token):
        try:
            return self._serializer.loads(token, max_age=self._max_age)
        except (BadSignature, SignatureExpired):
            return None
