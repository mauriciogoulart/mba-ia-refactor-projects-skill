"""Provas de integração das correções de segurança e dos contratos aprovados (CT-01 a CT-08)."""
import uuid

import pytest

ROTAS_PROTEGIDAS = [
    ("GET", "/tasks"), ("GET", "/tasks/1"), ("GET", "/tasks/search"), ("GET", "/tasks/stats"),
    ("POST", "/tasks"), ("PUT", "/tasks/1"), ("DELETE", "/tasks/999999"),
    ("GET", "/users"), ("GET", "/users/1"), ("GET", "/users/1/tasks"), ("PUT", "/users/1"),
    ("DELETE", "/users/999999"), ("GET", "/reports/summary"), ("GET", "/reports/user/1"),
    ("GET", "/categories"), ("POST", "/categories"), ("PUT", "/categories/1"),
    ("DELETE", "/categories/999999"),
]


def _sufixo():
    return uuid.uuid4().hex[:8]


def _novo_usuario(api, **extra):
    payload = {"name": "Usuario " + _sufixo(), "email": f"s{_sufixo()}@teste.com", "password": "segredo"}
    payload.update(extra)
    r = api.post("/users", payload)
    assert r.status_code == 201, r.text
    return r.json()


def _nova_categoria(api):
    r = api.post("/categories", {"name": "Cat " + _sufixo()})
    assert r.status_code == 201, r.text
    return r.json()


def _nova_task(api):
    r = api.post("/tasks", {"title": "Task " + _sufixo()})
    assert r.status_code == 201, r.text
    return r.json()


# ---------- CT-01 / CT-02 (F-002): autenticação ----------

@pytest.mark.parametrize("metodo,rota", ROTAS_PROTEGIDAS)
def test_rota_sem_token_retorna_401(api, metodo, rota):
    assert api.anonimo._req(metodo, rota, json={}).status_code == 401


@pytest.mark.parametrize("token", ["invalido", "fake-jwt-token-1"])
def test_token_invalido_ou_forjado_retorna_401(api, token):
    cabecalho = {"Authorization": f"Bearer {token}"}
    assert api.anonimo.get("/tasks", headers=cabecalho).status_code == 401
    assert api.anonimo.get("/users/1", headers=cabecalho).status_code == 401


def test_token_valido_acessa_rota_protegida(api):
    assert api.usuario.get("/tasks").status_code == 200
    assert api.usuario.get("/categories").status_code == 200


def test_rotas_publicas_continuam_abertas(api):
    assert api.anonimo.get("/").status_code == 200
    assert api.anonimo.get("/health").status_code == 200


# ---------- CT-03 (F-004): hash de senha fora das respostas ----------

def test_respostas_de_usuario_nao_trazem_password(api):
    criado = _novo_usuario(api)
    assert "password" not in criado
    assert "password" not in api.get(f"/users/{criado['id']}").json()
    assert "password" not in api.put(f"/users/{criado['id']}", {"name": "Outro Nome"}).json()
    login = api.anonimo.post("/login", {"email": criado["email"], "password": "segredo"})
    assert login.status_code == 200
    assert "password" not in login.json()["user"]


# ---------- CT-04 (F-007): privilégios ----------

def test_cadastro_publico_cria_apenas_usuario_comum(api):
    base = {"name": "Publico", "password": "segredo"}
    r = api.anonimo.post("/users", {**base, "email": f"p{_sufixo()}@teste.com"})
    assert r.status_code == 201
    assert r.json()["role"] == "user"
    assert api.anonimo.post("/users", {**base, "email": f"p{_sufixo()}@teste.com", "role": "admin"}).status_code == 403
    assert api.usuario.post("/users", {**base, "email": f"p{_sufixo()}@teste.com", "role": "admin"}).status_code == 403


def test_usuario_nao_altera_outro_usuario(api):
    alvo = _novo_usuario(api)
    assert api.usuario.put(f"/users/{alvo['id']}", {"name": "Invadido"}).status_code == 403
    assert api.get(f"/users/{alvo['id']}").json()["name"] == alvo["name"]


def test_usuario_edita_a_si_mesmo_sem_mudar_privilegio(api):
    usuario = _novo_usuario(api)
    login = api.anonimo.post("/login", {"email": usuario["email"], "password": "segredo"}).json()
    cabecalho = {"Authorization": "Bearer " + login["token"]}
    uid = usuario["id"]
    assert api.anonimo.put(f"/users/{uid}", {"name": "Novo Nome"}, headers=cabecalho).status_code == 200
    assert api.anonimo.put(f"/users/{uid}", {"role": "admin"}, headers=cabecalho).status_code == 403
    assert api.anonimo.put(f"/users/{uid}", {"active": False}, headers=cabecalho).status_code == 403
    assert api.get(f"/users/{uid}").json()["role"] == "user"


def test_admin_altera_privilegio(api):
    alvo = _novo_usuario(api)
    r = api.put(f"/users/{alvo['id']}", {"role": "manager"})
    assert r.status_code == 200
    assert r.json()["role"] == "manager"


# ---------- CT-05 (F-006): rotas destrutivas ----------

def test_remover_usuario_exige_admin(api):
    alvo = _novo_usuario(api)
    assert api.anonimo.delete(f"/users/{alvo['id']}").status_code == 401
    assert api.usuario.delete(f"/users/{alvo['id']}").status_code == 403
    assert api.get(f"/users/{alvo['id']}").status_code == 200
    assert api.delete(f"/users/{alvo['id']}").status_code == 200


def test_remover_categoria_exige_admin(api):
    categoria = _nova_categoria(api)
    assert api.anonimo.delete(f"/categories/{categoria['id']}").status_code == 401
    assert api.usuario.delete(f"/categories/{categoria['id']}").status_code == 403
    assert api.delete(f"/categories/{categoria['id']}").status_code == 200


def test_remover_task_exige_autenticacao(api):
    task = _nova_task(api)
    assert api.anonimo.delete(f"/tasks/{task['id']}").status_code == 401
    assert api.delete(f"/tasks/{task['id']}").status_code == 200


# ---------- CT-09 (F-029): dados de terceiros ----------

def _cabecalho_de(api, usuario):
    login = api.anonimo.post("/login", {"email": usuario["email"], "password": "segredo"})
    assert login.status_code == 200, login.text
    return {"Authorization": "Bearer " + login.json()["token"]}


def test_task_de_terceiro_nao_pode_ser_alterada_nem_removida(api):
    responsavel = _novo_usuario(api)
    task = api.post("/tasks", {"title": "Task " + _sufixo(), "user_id": responsavel["id"]}).json()
    assert api.usuario.put(f"/tasks/{task['id']}", {"status": "cancelled"}).status_code == 403
    assert api.usuario.delete(f"/tasks/{task['id']}").status_code == 403
    assert api.get(f"/tasks/{task['id']}").json()["status"] == "pending"


def test_responsavel_e_gestao_alteram_a_task(api):
    responsavel = _novo_usuario(api)
    cabecalho = _cabecalho_de(api, responsavel)
    task = api.post("/tasks", {"title": "Task " + _sufixo(), "user_id": responsavel["id"]}).json()
    assert api.anonimo.put(f"/tasks/{task['id']}", {"status": "done"}, headers=cabecalho).status_code == 200
    assert api.gerente.put(f"/tasks/{task['id']}", {"priority": 1}).status_code == 200
    assert api.anonimo.delete(f"/tasks/{task['id']}", headers=cabecalho).status_code == 200


@pytest.mark.parametrize("modelo", ["/users/{}", "/users/{}/tasks", "/reports/user/{}"])
def test_dados_de_usuario_so_para_o_proprio_ou_gestao(api, modelo):
    alvo = _novo_usuario(api)
    rota = modelo.format(alvo["id"])
    assert api.usuario.get(rota).status_code == 403
    assert api.anonimo.get(rota, headers=_cabecalho_de(api, alvo)).status_code == 200
    assert api.gerente.get(rota).status_code == 200
    assert api.get(rota).status_code == 200


@pytest.mark.parametrize("rota", ["/users", "/reports/summary"])
def test_visoes_gerais_so_para_gestao(api, rota):
    assert api.usuario.get(rota).status_code == 403
    assert api.gerente.get(rota).status_code == 200
    assert api.get(rota).status_code == 200


# ---------- CT-06 (F-002/F-012): CORS e proteções HTTP ----------

def test_cors_nao_libera_origem_externa(api):
    r = api.anonimo.get("/health", headers={"Origin": "http://evil.example"})
    assert "Access-Control-Allow-Origin" not in r.headers


def test_cabecalhos_de_seguranca_presentes(api):
    r = api.anonimo.get("/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"


def test_login_bloqueia_apos_falhas_repetidas(api):
    usuario = _novo_usuario(api)
    credencial = {"email": usuario["email"], "password": "senha-errada"}
    for _ in range(5):
        assert api.anonimo.post("/login", credencial).status_code == 401
    assert api.anonimo.post("/login", credencial).status_code == 429


# ---------- CT-07 (F-014): validação ----------

@pytest.mark.parametrize("campos", [{"name": ""}, {"active": "sim"}, {"email": "a@dominio"}])
def test_atualizar_usuario_rejeita_valor_invalido(api, campos):
    alvo = _novo_usuario(api)
    assert api.put(f"/users/{alvo['id']}", campos).status_code == 400


def test_categoria_rejeita_cor_e_nome_invalidos(api):
    assert api.post("/categories", {"name": "Cor ruim", "color": "vermelho"}).status_code == 400
    categoria = _nova_categoria(api)
    assert api.put(f"/categories/{categoria['id']}", {"color": "#12"}).status_code == 400
    assert api.put(f"/categories/{categoria['id']}", {"name": ""}).status_code == 400


def test_tipos_invalidos_retornam_400(api):
    task = _nova_task(api)
    assert api.post("/tasks", {"title": "Titulo valido", "priority": "alta"}).status_code == 400
    assert api.post("/tasks", {"title": 123}).status_code == 400
    assert api.put(f"/tasks/{task['id']}", {"priority": "alta"}).status_code == 400
    assert api.get("/tasks/search", params={"priority": "alta"}).status_code == 400
    assert api.get("/tasks/search", params={"user_id": "abc"}).status_code == 400


# ---------- CT-08 (F-018): paginação ----------

def test_paginacao_das_listagens(api):
    assert len(api.get("/tasks", params={"limit": 2}).json()) == 2
    assert len(api.get("/users", params={"limit": 1}).json()) == 1
    assert api.get("/tasks", params={"limit": 0}).status_code == 400
    assert api.get("/tasks", params={"offset": -1}).status_code == 400
    primeira = api.get("/tasks", params={"limit": 1}).json()[0]
    segunda = api.get("/tasks", params={"limit": 1, "offset": 1}).json()[0]
    assert primeira["id"] != segunda["id"]


# ---------- F-008 e F-009 ----------

def test_log_do_servidor_nao_registra_dados_pessoais(api):
    usuario = _novo_usuario(api, name="NomePessoal" + _sufixo())
    log = api.caminho_log.read_text(encoding="utf-8", errors="replace")
    assert usuario["name"] not in log
    assert usuario["email"] not in log


def test_senha_literal_antiga_do_seed_nao_funciona(api):
    assert api.anonimo.post("/login", {"email": "joao@email.com", "password": "1234"}).status_code == 401
