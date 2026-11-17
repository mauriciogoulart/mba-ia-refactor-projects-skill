"""Autenticação por token Bearer e autorização por perfil/propriedade."""
from functools import wraps

from flask import current_app, g, request

from services.erros import AppError
from services.regras import TIPO_ADMIN


def _usuario_do_token():
    cabecalho = request.headers.get("Authorization", "")
    if not cabecalho.startswith("Bearer "):
        return None
    loja = current_app.extensions["loja"]
    dados = loja.token_service.verificar(cabecalho[len("Bearer "):].strip())
    if not dados:
        return None
    return loja.usuario_service.identidade(dados.get("id"))


def exigir_autenticacao(*perfis):
    """Sem token válido ⇒ 401; perfil fora de `perfis` (quando informado) ⇒ 403."""
    def decorador(funcao):
        @wraps(funcao)
        def envoltorio(*args, **kwargs):
            usuario = _usuario_do_token()
            if usuario is None:
                raise AppError("Não autenticado", 401)
            if perfis and usuario["tipo"] not in perfis:
                raise AppError("Acesso negado", 403)
            g.usuario = usuario
            return funcao(*args, **kwargs)
        return envoltorio
    return decorador


def eh_admin():
    return g.usuario["tipo"] == TIPO_ADMIN


def garantir_proprio_ou_admin(usuario_id):
    if not eh_admin() and g.usuario["id"] != usuario_id:
        raise AppError("Acesso negado", 403)
