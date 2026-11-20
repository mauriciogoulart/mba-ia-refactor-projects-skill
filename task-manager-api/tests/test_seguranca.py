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


# ---------- CT-09 (F-029): leitura de tasks e atribuição (validação independente) ----------

def _usuario_com_task(api, titulo=None):
    usuario = _novo_usuario(api)
    corpo = {"title": titulo or "Task " + _sufixo(), "user_id": usuario["id"]}
    task = api.post("/tasks", corpo)
    assert task.status_code == 201, task.text
    return usuario, task.json(), _cabecalho_de(api, usuario)


def test_listagem_mostra_somente_as_proprias_tasks(api):
    _, propria, cabecalho = _usuario_com_task(api)
    _, alheia, _ = _usuario_com_task(api)
    ids = [t["id"] for t in api.anonimo.get("/tasks", headers=cabecalho).json()]
    assert ids == [propria["id"]]
    assert alheia["id"] not in ids


def test_acesso_direto_a_task_alheia_retorna_403(api):
    _, propria, cabecalho = _usuario_com_task(api)
    _, alheia, _ = _usuario_com_task(api)
    assert api.anonimo.get(f"/tasks/{alheia['id']}", headers=cabecalho).status_code == 403
    assert api.anonimo.get(f"/tasks/{propria['id']}", headers=cabecalho).status_code == 200
    assert api.gerente.get(f"/tasks/{alheia['id']}").status_code == 200
    assert api.get(f"/tasks/{alheia['id']}").status_code == 200
    assert api.anonimo.get("/tasks/999999", headers=cabecalho).status_code == 404


def test_busca_filtra_pelo_proprio_usuario(api):
    marcador = "busca" + _sufixo()
    dono, alheia, _ = _usuario_com_task(api, titulo="Alheia " + marcador)
    _, _, cabecalho = _usuario_com_task(api)
    assert api.anonimo.get("/tasks/search", params={"q": marcador}, headers=cabecalho).json() == []
    assert api.anonimo.get("/tasks/search", params={"user_id": dono["id"]}, headers=cabecalho).json() == []
    assert [t["id"] for t in api.gerente.get("/tasks/search", params={"q": marcador}).json()] == [alheia["id"]]


def test_estatisticas_consideram_somente_as_proprias_tasks(api):
    _, _, cabecalho = _usuario_com_task(api)
    _usuario_com_task(api)
    assert api.anonimo.get("/tasks/stats", headers=cabecalho).json()["total"] == 1
    assert api.gerente.get("/tasks/stats").json()["total"] > 1


def test_contagem_por_categoria_nao_revela_tasks_alheias(api):
    categoria = _nova_categoria(api)
    dono = _novo_usuario(api)
    assert api.post("/tasks", {"title": "Task " + _sufixo(), "user_id": dono["id"],
                               "category_id": categoria["id"]}).status_code == 201
    _, _, cabecalho = _usuario_com_task(api)

    def contagem(resposta):
        return next(c["task_count"] for c in resposta.json() if c["id"] == categoria["id"])

    assert contagem(api.anonimo.get("/categories", headers=cabecalho)) == 0
    assert contagem(api.gerente.get("/categories")) == 1


def test_usuario_comum_nao_atribui_task_a_terceiro(api):
    dono, propria, cabecalho = _usuario_com_task(api)
    outro = _novo_usuario(api)
    corpo = {"title": "Task " + _sufixo(), "user_id": outro["id"]}
    assert api.anonimo.post("/tasks", corpo, headers=cabecalho).status_code == 403
    assert api.anonimo.put(f"/tasks/{propria['id']}", {"user_id": outro["id"]}, headers=cabecalho).status_code == 403
    assert api.anonimo.put(f"/tasks/{propria['id']}", {"user_id": None}, headers=cabecalho).status_code == 403
    assert api.get(f"/tasks/{propria['id']}").json()["user_id"] == dono["id"]


def test_gestao_atribui_task_a_terceiro(api):
    dono, propria, _ = _usuario_com_task(api)
    outro = _novo_usuario(api)
    criada = api.gerente.post("/tasks", {"title": "Task " + _sufixo(), "user_id": outro["id"]})
    assert criada.status_code == 201
    assert criada.json()["user_id"] == outro["id"]
    transferida = api.gerente.put(f"/tasks/{propria['id']}", {"user_id": outro["id"]})
    assert transferida.status_code == 200
    assert transferida.json()["user_id"] == outro["id"]
    assert dono["id"] != outro["id"]


def test_task_criada_por_usuario_comum_fica_sob_sua_responsabilidade(api):
    dono = _novo_usuario(api)
    cabecalho = _cabecalho_de(api, dono)
    criada = api.anonimo.post("/tasks", {"title": "Task " + _sufixo()}, headers=cabecalho)
    assert criada.status_code == 201
    assert criada.json()["user_id"] == dono["id"]
    assert api.anonimo.get(f"/tasks/{criada.json()['id']}", headers=cabecalho).status_code == 200


@pytest.mark.parametrize("valor", [[], {}, 10 ** 30])
@pytest.mark.parametrize("campo", ["user_id", "category_id"])
def test_referencia_invalida_retorna_400(api, campo, valor):
    task = _nova_task(api)
    assert api.post("/tasks", {"title": "Titulo valido", campo: valor}).status_code == 400
    assert api.put(f"/tasks/{task['id']}", {campo: valor}).status_code == 400


def test_inteiros_gigantes_na_url_e_na_busca_nao_geram_500(api):
    gigante = 10 ** 30
    assert api.get(f"/tasks/{gigante}").status_code == 404
    assert api.get(f"/users/{gigante}").status_code == 404
    assert api.get("/tasks/search", params={"user_id": gigante}).status_code == 400
    assert api.get("/tasks/search", params={"priority": gigante}).status_code == 400
    assert api.get("/tasks", params={"offset": gigante}).status_code == 400


# ---------- Segunda validação independente: token vinculado à conta e ajustes ----------

def test_token_de_conta_excluida_nao_assume_a_conta_que_herda_o_id(api):
    conta_a = _novo_usuario(api)
    token_a = _cabecalho_de(api, conta_a)
    rota = f"/users/{conta_a['id']}"
    assert api.anonimo.get(rota, headers=token_a).status_code == 200
    assert api.delete(rota).status_code == 200
    assert api.anonimo.get(rota, headers=token_a).status_code == 401

    conta_b = _novo_usuario(api)
    assert conta_b["id"] == conta_a["id"]
    assert api.anonimo.get(rota, headers=token_a).status_code == 401
    assert api.anonimo.get("/tasks", headers=token_a).status_code == 401
    assert api.anonimo.put(rota, {"password": "senha-tomada"}, headers=token_a).status_code == 401
    assert api.anonimo.get(rota, headers=_cabecalho_de(api, conta_b)).status_code == 200


def test_token_antigo_deixa_de_valer_apos_troca_de_senha(api):
    usuario = _novo_usuario(api)
    antigo = _cabecalho_de(api, usuario)
    rota = f"/users/{usuario['id']}"
    assert api.anonimo.put(rota, {"password": "senha-nova"}, headers=antigo).status_code == 200
    assert api.anonimo.get(rota, headers=antigo).status_code == 401
    assert api.anonimo.post("/login", {"email": usuario["email"], "password": "segredo"}).status_code == 401
    novo = api.anonimo.post("/login", {"email": usuario["email"], "password": "senha-nova"})
    assert novo.status_code == 200
    assert api.anonimo.get(rota, headers={"Authorization": "Bearer " + novo.json()["token"]}).status_code == 200


def test_titulo_com_surrogate_isolado_retorna_400(api):
    corpo = '{"title": "Titulo \\ud800 invalido"}'
    r = api.post("/tasks", data=corpo, headers={"Content-Type": "application/json"})
    assert r.status_code == 400


@pytest.mark.parametrize("valor", [2.5, True])
def test_prioridade_nao_inteira_retorna_400(api, valor):
    task = _nova_task(api)
    assert api.post("/tasks", {"title": "Titulo valido", "priority": valor}).status_code == 400
    assert api.put(f"/tasks/{task['id']}", {"priority": valor}).status_code == 400


@pytest.mark.parametrize("valor", [0, 999999])
@pytest.mark.parametrize("campo", ["user_id", "category_id"])
def test_referencia_zero_ou_inexistente_retorna_404(api, campo, valor):
    task = _nova_task(api)
    assert api.post("/tasks", {"title": "Titulo valido", campo: valor}).status_code == 404
    assert api.put(f"/tasks/{task['id']}", {campo: valor}).status_code == 404


def test_usuario_comum_nao_atribui_task_ao_id_zero(api):
    _, propria, cabecalho = _usuario_com_task(api)
    assert api.anonimo.post("/tasks", {"title": "Task " + _sufixo(), "user_id": 0}, headers=cabecalho).status_code == 403
    assert api.anonimo.put(f"/tasks/{propria['id']}", {"user_id": 0}, headers=cabecalho).status_code == 403


def test_estatisticas_por_status_e_atraso_no_escopo_do_usuario(api):
    dono = _novo_usuario(api)
    outro = _novo_usuario(api)
    for responsavel, status, vencimento in ((dono, "pending", "2000-01-01"), (dono, "in_progress", None),
                                            (dono, "done", "2000-01-01"), (dono, "cancelled", None),
                                            (outro, "pending", "2000-01-01"), (outro, "in_progress", "2000-01-01")):
        corpo = {"title": "Task " + _sufixo(), "user_id": responsavel["id"], "status": status}
        if vencimento:
            corpo["due_date"] = vencimento
        assert api.post("/tasks", corpo).status_code == 201
    stats = api.anonimo.get("/tasks/stats", headers=_cabecalho_de(api, dono)).json()
    assert stats == {"total": 4, "pending": 1, "in_progress": 1, "done": 1, "cancelled": 1,
                     "overdue": 1, "completion_rate": 25.0}


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
