"""Provas das mudanças de contrato aprovadas (CT-01…CT-07, relatório reports/audit-project-3.md).

Cada teste falha contra o código original (sem autenticação, hash exposto, CORS aberto,
erros 500) e passa no código refatorado. Usam ids inexistentes ou dados criados pelo
próprio teste para não depender da ordem de execução.
"""
import uuid

from conftest import ORIGEM_PERMITIDA

TOKEN_INVALIDO = {"Authorization": "Bearer token-invalido"}


def _sufixo():
    return uuid.uuid4().hex[:8]


def _criar_usuario(api, **extra):
    payload = {"name": "Usuario " + _sufixo(), "email": f"c{_sufixo()}@teste.com",
               "password": "segredo"}
    payload.update(extra)
    r = api.post("/users", payload)
    assert r.status_code == 201, r.text
    return {**r.json(), "password": payload["password"]}


def _token(anonimo, usuario):
    r = anonimo.post("/login", {"email": usuario["email"], "password": usuario["password"]})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


# ---------- CT-01: token assinado ----------

def test_ct01_token_forjado_e_rejeitado(anonimo):
    forjado = {"Authorization": "Bearer fake-jwt-token-1"}
    assert anonimo.get("/tasks", headers=forjado).status_code == 401
    assert anonimo.get("/users/1", headers=forjado).status_code == 401


# ---------- CT-02: rotas de dados exigem token ----------

ROTAS_PROTEGIDAS = [
    ("GET", "/tasks"), ("GET", "/tasks/1"), ("GET", "/tasks/search"), ("GET", "/tasks/stats"),
    ("POST", "/tasks"), ("PUT", "/tasks/999999"), ("DELETE", "/tasks/999999"),
    ("GET", "/users"), ("GET", "/users/1"), ("GET", "/users/1/tasks"),
    ("GET", "/categories"), ("POST", "/categories"), ("PUT", "/categories/999999"),
    ("DELETE", "/categories/999999"),
    ("GET", "/reports/summary"), ("GET", "/reports/user/1"),
]


def test_ct02_rotas_de_dados_exigem_token(anonimo):
    for metodo, rota in ROTAS_PROTEGIDAS:
        corpo = {} if metodo in ("POST", "PUT") else None
        assert anonimo._req(metodo, rota, json=corpo).status_code == 401, (metodo, rota)
        r = anonimo._req(metodo, rota, json=corpo, headers=TOKEN_INVALIDO)
        assert r.status_code == 401, (metodo, rota)


def test_ct02_rotas_publicas_continuam_abertas(anonimo):
    assert anonimo.get("/").status_code == 200
    assert anonimo.get("/health").status_code == 200


def test_ct02_token_valido_libera_acesso(api):
    assert api.get("/tasks").status_code == 200
    assert api.get("/reports/summary").status_code == 200


# ---------- CT-03: alteração e exclusão de usuários ----------

def test_ct03_alterar_e_excluir_usuario_exige_permissao(api, anonimo):
    alvo = _criar_usuario(api)
    comum = _criar_usuario(api)
    token_comum = _token(anonimo, comum)

    assert anonimo.put(f"/users/{alvo['id']}", {"name": "Invasor"}).status_code == 401
    assert anonimo.put(f"/users/{alvo['id']}", {"name": "Invasor"},
                       headers=token_comum).status_code == 403
    assert anonimo.put(f"/users/{comum['id']}", {"role": "admin"},
                       headers=token_comum).status_code == 403
    assert anonimo.put(f"/users/{comum['id']}", {"active": False},
                       headers=token_comum).status_code == 403
    r = anonimo.put(f"/users/{comum['id']}", {"name": "Proprio Nome"}, headers=token_comum)
    assert r.status_code == 200
    assert r.json()["name"] == "Proprio Nome"

    assert anonimo.delete(f"/users/{alvo['id']}", headers=token_comum).status_code == 403
    assert anonimo.delete(f"/users/{alvo['id']}").status_code == 401
    assert api.get(f"/users/{alvo['id']}").status_code == 200
    assert api.delete(f"/users/{alvo['id']}").status_code == 200


# ---------- CT-04: role no cadastro ----------

def test_ct04_cadastro_anonimo_nao_define_role_privilegiado(api, anonimo):
    base = {"name": "Fulano", "password": "abcd"}
    r = anonimo.post("/users", {**base, "email": f"a{_sufixo()}@teste.com", "role": "admin"})
    assert r.status_code == 403
    r = anonimo.post("/users", {**base, "email": f"m{_sufixo()}@teste.com", "role": "manager"})
    assert r.status_code == 403

    r = anonimo.post("/users", {**base, "email": f"u{_sufixo()}@teste.com"})
    assert r.status_code == 201
    assert r.json()["role"] == "user"

    r = api.post("/users", {**base, "email": f"g{_sufixo()}@teste.com", "role": "manager"})
    assert r.status_code == 201
    assert r.json()["role"] == "manager"


# ---------- CT-05: hash da senha fora das respostas ----------

def test_ct05_password_ausente_nas_respostas(api, anonimo):
    usuario = _criar_usuario(api)
    r = api.post("/users", {"name": "Sem Hash", "email": f"h{_sufixo()}@teste.com", "password": "abcd"})
    assert r.status_code == 201
    assert "password" not in r.json()

    r = api.get(f"/users/{usuario['id']}")
    assert r.status_code == 200
    assert "password" not in r.json()

    r = api.put(f"/users/{usuario['id']}", {"name": "Outro Nome"})
    assert r.status_code == 200
    assert "password" not in r.json()

    r = anonimo.post("/login", {"email": usuario["email"], "password": "segredo"})
    assert r.status_code == 200
    assert "password" not in r.json()["user"]


# ---------- CT-06: CORS restrito ----------

def test_ct06_cors_somente_para_origens_configuradas(anonimo):
    r = anonimo.get("/health", headers={"Origin": "http://malicioso.local"})
    assert "Access-Control-Allow-Origin" not in r.headers
    r = anonimo.get("/health", headers={"Origin": ORIGEM_PERMITIDA})
    assert r.headers.get("Access-Control-Allow-Origin") == ORIGEM_PERMITIDA


# ---------- CT-07: entrada com tipo inválido ⇒ 400 ----------

def test_ct07_tipo_invalido_retorna_400(api):
    r = api.post("/tasks", {"title": "Titulo valido"})
    assert r.status_code == 201
    tid = r.json()["id"]
    cat = api.post("/categories", {"name": "Cat " + _sufixo()})
    assert cat.status_code == 201
    cid = cat.json()["id"]

    casos = [
        ("POST", "/tasks", {"title": "Titulo valido", "priority": "5"}),
        ("POST", "/tasks", {"title": 12345}),
        ("POST", "/tasks", {"title": "Titulo valido", "tags": [1, 2]}),
        ("PUT", f"/tasks/{tid}", {"priority": "2"}),
        ("PUT", f"/tasks/{tid}", {"title": None}),
        ("POST", "/users", {"name": "X", "email": 123, "password": "abcd"}),
        ("POST", "/login", {"email": "joao@email.com", "password": 1234}),
    ]
    for metodo, rota, corpo in casos:
        r = api._req(metodo, rota, json=corpo)
        assert r.status_code == 400, (metodo, rota, corpo)
        assert "error" in r.json()

    for parametro in ("priority", "user_id"):
        r = api.get("/tasks/search", params={parametro: "abc"})
        assert r.status_code == 400, parametro
        assert "error" in r.json()

    r = api.put(f"/categories/{cid}", data="null", headers={"Content-Type": "application/json"})
    assert r.status_code == 400
    assert "error" in r.json()


def test_c06_validacoes_adicionais(api):
    usuario = _criar_usuario(api)
    assert api.put(f"/users/{usuario['id']}", {"name": ""}).status_code == 400
    assert api.put(f"/users/{usuario['id']}", {"active": "nao"}).status_code == 400
    assert api.post("/categories", {"name": "Cat " + _sufixo(), "color": "vermelho"}).status_code == 400
    r = api.post("/users", {"name": "Fulano", "email": f"x{_sufixo()}@semdominio", "password": "abcd"})
    assert r.status_code == 400
