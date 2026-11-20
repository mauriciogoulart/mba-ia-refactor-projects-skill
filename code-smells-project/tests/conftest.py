"""Fixtures dos testes de fumaça (caixa-preta, via HTTP).

A aplicação é copiada para um diretório temporário e iniciada com
`python app.py`, para que o banco `loja.db` real nunca seja alterado.
Os testes dependem apenas do contrato HTTP, não da estrutura interna do código.
"""
import os
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

DIR_PROJETO = Path(__file__).resolve().parent.parent
PORTA = 5000
URL_BASE = f"http://127.0.0.1:{PORTA}"
IGNORAR = shutil.ignore_patterns(
    "tests", ".venv", "venv", "__pycache__", "*.pyc", "*.db",
    "instance", ".pytest_cache", "node_modules",
)


def _porta_em_uso(porta):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", porta)) == 0


def _encerrar(proc):
    """Encerra o processo e seus filhos (o reloader do Flask cria um filho)."""
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       capture_output=True)
    else:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    proc.wait(timeout=10)


class Cliente:
    def __init__(self, base):
        self.base = base

    def _req(self, metodo, caminho, **kw):
        return requests.request(metodo, self.base + caminho, timeout=10, **kw)

    def get(self, caminho, **kw):
        return self._req("GET", caminho, **kw)

    def post(self, caminho, json=None, **kw):
        return self._req("POST", caminho, json=json, **kw)

    def put(self, caminho, json=None, **kw):
        return self._req("PUT", caminho, json=json, **kw)

    def delete(self, caminho, **kw):
        return self._req("DELETE", caminho, **kw)


@pytest.fixture(scope="session")
def credenciais():
    """Senhas de seed aleatórias por execução, lidas pela aplicação via ambiente."""
    return {"admin": secrets.token_urlsafe(12), "cliente": secrets.token_urlsafe(12)}


@pytest.fixture(scope="session")
def ambiente_app(tmp_path_factory):
    raiz = tmp_path_factory.mktemp("app")
    return {"raiz": raiz, "destino": raiz / "projeto", "log": raiz / "servidor.log",
            "banco": raiz / "projeto" / "loja.db"}


@pytest.fixture(scope="session")
def caminho_banco(api, ambiente_app):
    return ambiente_app["banco"]


@pytest.fixture(scope="session")
def log_servidor(api, ambiente_app):
    return ambiente_app["log"]


@pytest.fixture(scope="session")
def admin_headers(api, credenciais):
    """Cabeçalho Authorization do admin de seed (token emitido pelo POST /login)."""
    r = api.post("/login", {"email": "admin@loja.com", "senha": credenciais["admin"]})
    token = r.json().get("dados", {}).get("token", "") if r.status_code == 200 else ""
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def api(ambiente_app, credenciais):
    if _porta_em_uso(PORTA):
        pytest.exit(f"Porta {PORTA} já está em uso; encerre o processo e rode novamente.",
                    returncode=2)

    destino = ambiente_app["destino"]
    shutil.copytree(DIR_PROJETO, destino, ignore=IGNORAR)

    caminho_log = ambiente_app["log"]
    log = caminho_log.open("w", encoding="utf-8")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1",
           "SECRET_KEY": secrets.token_hex(32),
           "SEED_ADMIN_PASSWORD": credenciais["admin"],
           "SEED_CLIENTE_PASSWORD": credenciais["cliente"],
           "DB_PATH": str(ambiente_app["banco"])}
    proc = subprocess.Popen(
        [sys.executable, "app.py"], cwd=destino, env=env,
        stdout=log, stderr=subprocess.STDOUT,
        start_new_session=(os.name != "nt"),
    )
    try:
        limite = time.time() + 30
        while time.time() < limite:
            if proc.poll() is not None:
                pytest.exit("A aplicação encerrou ao iniciar:\n"
                            + caminho_log.read_text(encoding="utf-8"), returncode=2)
            try:
                if requests.get(URL_BASE + "/health", timeout=1).status_code == 200:
                    break
            except requests.RequestException:
                time.sleep(0.3)
        else:
            pytest.exit("Timeout aguardando a aplicação subir em /health.", returncode=2)
        yield Cliente(URL_BASE)
    finally:
        _encerrar(proc)
        log.close()
