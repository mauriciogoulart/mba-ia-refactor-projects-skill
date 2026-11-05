"""Proteções HTTP básicas: cabeçalhos de segurança e limite de tentativas de login."""
import threading
import time
from functools import wraps

from flask import current_app, request

from errors import AppError

_CABECALHOS_SEGURANCA = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
}


class LimitadorTentativas:
    """Janela deslizante em memória, por origem. O estado vive nesta instância (criada no app)."""

    def __init__(self, maximo, janela_segundos):
        self._maximo = maximo
        self._janela = janela_segundos
        self._tentativas = {}
        self._trava = threading.Lock()

    def permitir(self, chave):
        agora = time.monotonic()
        with self._trava:
            recentes = [t for t in self._tentativas.get(chave, []) if agora - t < self._janela]
            if len(recentes) >= self._maximo:
                self._tentativas[chave] = recentes
                return False
            recentes.append(agora)
            self._tentativas[chave] = recentes
            return True


def registrar_protecoes_http(app, max_tentativas, janela_segundos):
    app.extensions["limitador_login"] = LimitadorTentativas(max_tentativas, janela_segundos)

    @app.after_request
    def _adicionar_cabecalhos(resposta):
        for nome, valor in _CABECALHOS_SEGURANCA.items():
            resposta.headers.setdefault(nome, valor)
        return resposta


def limitar_tentativas(funcao):
    @wraps(funcao)
    def limitada(*args, **kwargs):
        limitador = current_app.extensions["limitador_login"]
        if not limitador.permitir(request.remote_addr):
            raise AppError("Muitas tentativas. Tente novamente mais tarde", 429)
        return funcao(*args, **kwargs)
    return limitada
