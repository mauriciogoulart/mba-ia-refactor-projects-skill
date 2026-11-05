"""Autenticação por token assinado (Bearer) e autorização por perfil."""
from functools import wraps

from flask import current_app, g, request
from itsdangerous import BadSignature, URLSafeTimedSerializer

from errors import AppError

_SALT = "auth-token"


def _serializador():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=_SALT)


def emitir_token(usuario):
    return _serializador().dumps({"id": usuario["id"], "tipo": usuario["tipo"]})


def identificar_usuario():
    cabecalho = request.headers.get("Authorization", "")
    if not cabecalho.startswith("Bearer "):
        return None
    try:
        return _serializador().loads(
            cabecalho[len("Bearer "):], max_age=current_app.config["TOKEN_MAX_AGE_SEGUNDOS"]
        )
    except BadSignature:
        return None


def exigir_perfil(*perfis):
    def decorador(funcao):
        @wraps(funcao)
        def protegida(*args, **kwargs):
            usuario = identificar_usuario()
            if usuario is None:
                raise AppError("Não autenticado", 401)
            if perfis and usuario.get("tipo") not in perfis:
                raise AppError("Sem permissão", 403)
            g.usuario = usuario
            return funcao(*args, **kwargs)
        return protegida
    return decorador
