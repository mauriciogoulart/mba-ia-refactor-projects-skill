"""Testes de prova (integração, via HTTP) das correções de segurança e dos contratos aprovados.

Cada teste cita o CT-xx/F-xxx do relatório reports/audit-project-1.md que comprova.
"""
import sqlite3
import uuid

import pytest

SEM = {}
INVALIDO = {"Authorization": "Bearer token-invalido"}


def _sufixo():
    return uuid.uuid4().hex[:8]


@pytest.fixture
def cliente(api):
    """Cliente criado pelo cadastro público e autenticado pelo próprio login."""
    email, senha = f"c{_sufixo()}@teste.com", "segredo-" + _sufixo()
    r = api.post("/usuarios", {"nome": "Cliente Prova", "email": email, "senha": senha})
    assert r.status_code == 201, r.text
    uid = r.json()["dados"]["id"]
    login = api.post("/login", {"email": email, "senha": senha})
    token = login.json().get("dados", {}).get("token", "") if login.status_code == 200 else ""
    return {"id": uid, "email": email, "senha": senha, "headers": {"Authorization": f"Bearer {token}"}}


def _produto(api, admin_headers, estoque=5, preco=10.0, nome=None):
    r = api.post("/produtos", {"nome": nome or "Prova" + _sufixo(), "descricao": "x", "preco": preco,
                               "estoque": estoque, "categoria": "geral"}, headers=admin_headers)
    assert r.status_code == 201, r.text
    return r.json()["dados"]["id"]


# ---------- CT-01 / F-005: execução de SQL removida ----------

def test_ct01_admin_query_removida(api, admin_headers):
    for headers in (SEM, admin_headers):
        r = api.post("/admin/query", {"sql": "SELECT 1 AS x"}, headers=headers)
        assert r.status_code in (404, 405)


# ---------- CT-02 / F-004: reset exige admin (positivo só na execução local V4, banco descartável) ----------

def test_ct02_reset_db_exige_admin(api, cliente):
    assert api.post("/admin/reset-db", headers=SEM).status_code == 401
    assert api.post("/admin/reset-db", headers=INVALIDO).status_code == 401
    assert api.post("/admin/reset-db", headers=cliente["headers"]).status_code == 403
    assert api.get("/health").json()["counts"]["produtos"] >= 10  # nada foi apagado


# ---------- CT-03 / F-004: relatório financeiro exige admin ----------

def test_ct03_relatorio_exige_admin(api, admin_headers, cliente):
    assert api.get("/relatorios/vendas", headers=SEM).status_code == 401
    assert api.get("/relatorios/vendas", headers=INVALIDO).status_code == 401
    assert api.get("/relatorios/vendas", headers=cliente["headers"]).status_code == 403
    assert api.get("/relatorios/vendas", headers=admin_headers).status_code == 200


# ---------- CT-04 / F-003: escrita de produtos exige admin; leitura segue pública ----------

def test_ct04_escrita_de_produtos_exige_admin(api, admin_headers, cliente):
    corpo = {"nome": "Bloqueado", "preco": 1, "estoque": 1}
    assert api.post("/produtos", corpo, headers=SEM).status_code == 401
    assert api.post("/produtos", corpo, headers=cliente["headers"]).status_code == 403
    pid = _produto(api, admin_headers)
    assert api.put(f"/produtos/{pid}", corpo, headers=SEM).status_code == 401
    assert api.put(f"/produtos/{pid}", corpo, headers=cliente["headers"]).status_code == 403
    assert api.delete(f"/produtos/{pid}", headers=SEM).status_code == 401
    assert api.delete(f"/produtos/{pid}", headers=cliente["headers"]).status_code == 403
    assert api.get(f"/produtos/{pid}").status_code == 200
    assert api.get("/produtos").status_code == 200


# ---------- CT-05 / F-003: usuários exigem token (lista: admin; por id: próprio ou admin) ----------

def test_ct05_usuarios_exigem_token(api, admin_headers, cliente):
    assert api.get("/usuarios", headers=SEM).status_code == 401
    assert api.get("/usuarios", headers=cliente["headers"]).status_code == 403
    assert api.get(f"/usuarios/{cliente['id']}", headers=SEM).status_code == 401
    assert api.get("/usuarios/1", headers=cliente["headers"]).status_code == 403
    assert api.get(f"/usuarios/{cliente['id']}", headers=cliente["headers"]).status_code == 200
    assert api.get(f"/usuarios/{cliente['id']}", headers=admin_headers).status_code == 200


# ---------- CT-06 / F-003: pedidos exigem token e propriedade ----------

def test_ct06_pedidos_exigem_token_e_propriedade(api, admin_headers, cliente):
    pid = _produto(api, admin_headers)
    proprio = {"usuario_id": cliente["id"], "itens": [{"produto_id": pid, "quantidade": 1}]}
    alheio = {"usuario_id": 1, "itens": [{"produto_id": pid, "quantidade": 1}]}
    assert api.post("/pedidos", proprio, headers=SEM).status_code == 401
    assert api.post("/pedidos", alheio, headers=cliente["headers"]).status_code == 403
    r = api.post("/pedidos", proprio, headers=cliente["headers"])
    assert r.status_code == 201
    pedido_id = r.json()["dados"]["pedido_id"]

    assert api.get("/pedidos", headers=SEM).status_code == 401
    assert api.get("/pedidos", headers=cliente["headers"]).status_code == 403
    assert api.get(f"/pedidos/usuario/{cliente['id']}", headers=SEM).status_code == 401
    assert api.get("/pedidos/usuario/1", headers=cliente["headers"]).status_code == 403
    assert api.get(f"/pedidos/usuario/{cliente['id']}", headers=cliente["headers"]).status_code == 200

    status = {"status": "aprovado"}
    assert api.put(f"/pedidos/{pedido_id}/status", status, headers=SEM).status_code == 401
    assert api.put(f"/pedidos/{pedido_id}/status", status, headers=cliente["headers"]).status_code == 403
    assert api.put(f"/pedidos/{pedido_id}/status", status, headers=admin_headers).status_code == 200


# ---------- CT-07 / F-003: login emite token verificável ----------

def test_ct07_login_emite_token_que_autentica(api, cliente):
    r = api.post("/login", {"email": cliente["email"], "senha": cliente["senha"]})
    assert r.status_code == 200
    token = r.json()["dados"].get("token")
    assert isinstance(token, str) and token
    assert api.get(f"/usuarios/{cliente['id']}",
                   headers={"Authorization": f"Bearer {token}"}).status_code == 200
    assert api.get(f"/usuarios/{cliente['id']}",
                   headers={"Authorization": f"Bearer {token}x"}).status_code == 401


# ---------- CT-08 / CT-09 / F-006: sem senha nem configuração nas respostas ----------

def test_ct08_usuarios_sem_campo_senha(api, admin_headers, cliente):
    lista = api.get("/usuarios", headers=admin_headers).json()["dados"]
    assert lista and all("senha" not in u for u in lista)
    proprio = api.get(f"/usuarios/{cliente['id']}", headers=cliente["headers"]).json()["dados"]
    assert "senha" not in proprio
    assert proprio["email"] == cliente["email"]


def test_ct09_health_sem_segredos(api):
    corpo = api.get("/health").json()
    for chave in ("secret_key", "db_path", "debug"):
        assert chave not in corpo
    assert corpo["status"] == "ok" and corpo["database"] == "connected" and "counts" in corpo


# ---------- CT-10 / F-016: CORS restrito; cabeçalhos e limite de login ----------

def test_ct10_cors_nao_libera_origem_arbitraria(api):
    r = api.get("/produtos", headers={"Origin": "http://evil.example"})
    assert r.status_code == 200
    assert "Access-Control-Allow-Origin" not in r.headers


def test_f016_cabecalhos_e_limite_de_tentativas_de_login(api, cliente):
    r = api.get("/")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    status = [api.post("/login", {"email": cliente["email"], "senha": "errada"}).status_code for _ in range(6)]
    assert status[:5] == [401] * 5 and status[5] == 429


# ---------- CT-11 / F-025: status de pedido inexistente ----------

def test_ct11_status_de_pedido_inexistente_retorna_404(api, admin_headers):
    r = api.put("/pedidos/99999999/status", {"status": "aprovado"}, headers=admin_headers)
    assert r.status_code == 404
    assert r.json()["sucesso"] is False


# ---------- CT-12 / F-021: e-mail único e usuário existente no pedido ----------

def test_ct12_integridade_email_unico_e_usuario_existente(api, admin_headers, cliente):
    r = api.post("/usuarios", {"nome": "Duplicado", "email": cliente["email"], "senha": "outra"})
    assert r.status_code == 400
    pid = _produto(api, admin_headers)
    r = api.post("/pedidos", {"usuario_id": 99999999, "itens": [{"produto_id": pid, "quantidade": 1}]},
                 headers=admin_headers)
    assert r.status_code == 400
    assert api.get(f"/produtos/{pid}").json()["dados"]["estoque"] == 5


# ---------- F-007: senhas armazenadas com hash ----------

def test_f007_senhas_armazenadas_com_hash(api, cliente, caminho_banco):
    with sqlite3.connect(caminho_banco) as conexao:
        do_cliente = conexao.execute("SELECT senha FROM usuarios WHERE email = ?", (cliente["email"],)).fetchone()[0]
        do_admin = conexao.execute("SELECT senha FROM usuarios WHERE email = 'admin@loja.com'").fetchone()[0]
    for armazenada in (do_cliente, do_admin):
        assert armazenada.startswith(("scrypt:", "pbkdf2:"))
    assert cliente["senha"] not in do_cliente


# ---------- F-008: SQL injection ----------

def test_f008_login_nao_aceita_sql_injection(api):
    for email in ("admin@loja.com' --", "x' OR '1'='1' --"):
        r = api.post("/login", {"email": email, "senha": "qualquer"})
        assert r.status_code == 401


def test_f008_texto_com_aspas_e_tratado_como_dado(api, admin_headers):
    nome = "D'Avila " + _sufixo()
    pid = _produto(api, admin_headers, nome=nome)
    assert api.get(f"/produtos/{pid}").json()["dados"]["nome"] == nome
    r = api.get("/produtos/busca", params={"q": "D'Avila"})
    assert r.status_code == 200
    assert any(p["id"] == pid for p in r.json()["dados"])
    r = api.get("/produtos/busca", params={"q": "' OR 1=1 --"})
    assert r.status_code == 200 and r.json()["total"] == 0


# ---------- F-010: validação de entrada ----------

def test_f010_quantidade_invalida_nao_altera_estoque(api, admin_headers, cliente):
    pid = _produto(api, admin_headers, estoque=5)
    for quantidade in (-3, 0, "2", 1.5):
        r = api.post("/pedidos", {"usuario_id": cliente["id"], "itens": [{"produto_id": pid, "quantidade": quantidade}]},
                     headers=cliente["headers"])
        assert r.status_code == 400, quantidade
    assert api.get(f"/produtos/{pid}").json()["dados"]["estoque"] == 5


def test_f010_tipos_invalidos_e_corpo_ausente_retornam_400(api, admin_headers):
    r = api.post("/produtos", {"nome": "Texto", "preco": "abc", "estoque": 1}, headers=admin_headers)
    assert r.status_code == 400
    r = api.post("/produtos", {"nome": "Texto", "preco": 1, "estoque": "muito"}, headers=admin_headers)
    assert r.status_code == 400
    pid = _produto(api, admin_headers)
    r = api.put(f"/produtos/{pid}", {"nome": "Ok nome", "preco": 1, "estoque": 1, "categoria": "inexistente"},
                headers=admin_headers)
    assert r.status_code == 400
    assert api.post("/login", None).status_code == 400


# ---------- F-011: e-mail não vai para o log ----------

def test_f011_email_nao_aparece_no_log(api, cliente, log_servidor):
    api.post("/login", {"email": cliente["email"], "senha": cliente["senha"]})
    api.post("/login", {"email": cliente["email"], "senha": "errada"})
    conteudo = log_servidor.read_text(encoding="utf-8", errors="replace")
    assert cliente["email"] not in conteudo
