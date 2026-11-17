"""Proteções HTTP: cabeçalhos de segurança, CORS restrito e limite de tentativas de login."""
import threading
import time

from flask_cors import CORS

CABECALHOS_SEGURANCA = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
}


class LimitadorDeLogin:
    """Conta falhas de login por chave (IP + e-mail) numa janela de tempo. Criado no composition root."""

    def __init__(self, max_tentativas, janela_segundos, relogio=time.monotonic):
        self._max = max_tentativas
        self._janela = janela_segundos
        self._relogio = relogio
        self._falhas = {}
        self._trava = threading.Lock()

    def _recentes(self, chave):
        limite = self._relogio() - self._janela
        return [t for t in self._falhas.get(chave, []) if t > limite]

    def bloqueado(self, chave):
        with self._trava:
            return len(self._recentes(chave)) >= self._max

    def registrar_falha(self, chave):
        with self._trava:
            self._falhas[chave] = self._recentes(chave) + [self._relogio()]

    def limpar(self, chave):
        with self._trava:
            self._falhas.pop(chave, None)


def registrar_protecoes_http(app, settings):
    if settings.CORS_ORIGINS:
        CORS(app, origins=settings.CORS_ORIGINS)

    @app.after_request
    def _cabecalhos(resposta):
        for nome, valor in CABECALHOS_SEGURANCA.items():
            resposta.headers.setdefault(nome, valor)
        return resposta
