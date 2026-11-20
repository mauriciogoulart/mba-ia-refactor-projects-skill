"""Fixtures dos testes de fumaça (caixa-preta, via HTTP).

A aplicação é copiada para um diretório temporário, populada com `python seed.py`
e iniciada com `python app.py`, para que o banco real (`instance/tasks.db`)
nunca seja alterado. Os testes dependem apenas do contrato HTTP, não da
estrutura interna do código.
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
SENHA_ADMIN = os.environ.get("SEED_ADMIN_PASSWORD") or secrets.token_urlsafe(16)
SENHA_USUARIO = os.environ.get("SEED_USER_PASSWORD") or secrets.token_urlsafe(16)
SENHA_MANAGER = os.environ.get("SEED_MANAGER_PASSWORD") or secrets.token_urlsafe(16)


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
    def __init__(self, base, token=None):
        self.base = base
        self.token = token

    def _req(self, metodo, caminho, headers=None, **kw):
        cabecalhos = dict(headers or {})
        if self.token:
            cabecalhos.setdefault("Authorization", f"Bearer {self.token}")
        return requests.request(metodo, self.base + caminho, headers=cabecalhos, timeout=10, **kw)

    def get(self, caminho, **kw):
        return self._req("GET", caminho, **kw)

    def post(self, caminho, json=None, **kw):
        return self._req("POST", caminho, json=json, **kw)

    def put(self, caminho, json=None, **kw):
        return self._req("PUT", caminho, json=json, **kw)

    def delete(self, caminho, **kw):
        return self._req("DELETE", caminho, **kw)


def _obter_token(email, senha):
    r = requests.post(URL_BASE + "/login", json={"email": email, "password": senha}, timeout=10)
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture(scope="session")
def api(tmp_path_factory):
    if _porta_em_uso(PORTA):
        pytest.exit(f"Porta {PORTA} já está em uso; encerre o processo e rode novamente.",
                    returncode=2)

    raiz = tmp_path_factory.mktemp("app")
    destino = raiz / "projeto"
    shutil.copytree(DIR_PROJETO, destino, ignore=IGNORAR)

    caminho_log = raiz / "servidor.log"
    log = caminho_log.open("w", encoding="utf-8")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1",
           "SECRET_KEY": secrets.token_hex(32), "SEED_ADMIN_PASSWORD": SENHA_ADMIN,
           "SEED_USER_PASSWORD": SENHA_USUARIO, "SEED_MANAGER_PASSWORD": SENHA_MANAGER}
    subprocess.run([sys.executable, "seed.py"], cwd=destino, env=env,
                   stdout=log, stderr=subprocess.STDOUT, check=True, timeout=60)
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
        cliente = Cliente(URL_BASE, token=_obter_token("joao@email.com", SENHA_ADMIN))
        cliente.anonimo = Cliente(URL_BASE)
        cliente.usuario = Cliente(URL_BASE, token=_obter_token("maria@email.com", SENHA_USUARIO))
        cliente.gerente = Cliente(URL_BASE, token=_obter_token("pedro@email.com", SENHA_MANAGER))
        cliente.senha_admin = SENHA_ADMIN
        cliente.caminho_log = caminho_log
        yield cliente
    finally:
        _encerrar(proc)
        log.close()
