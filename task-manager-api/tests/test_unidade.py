"""Provas de unidade das correções (configuração, senha, token, services e estrutura)."""
import hashlib
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture
def app_memoria():
    from app import create_app
    from config.settings import Settings
    from database import db

    aplicacao = create_app(Settings({"SECRET_KEY": "chave-de-teste", "DATABASE_URL": "sqlite:///:memory:"}))
    with aplicacao.app_context():
        yield aplicacao
        db.session.remove()
        db.drop_all()


# ---------- F-001 e F-003: configuração ----------

def test_configuracao_padrao_sem_debug_e_sem_bind_publico():
    from config.settings import Settings

    settings = Settings({})
    assert settings.DEBUG is False
    assert settings.HOST == "127.0.0.1"


def test_secret_key_vem_do_ambiente():
    from config.settings import Settings

    assert Settings({"SECRET_KEY": "valor-do-ambiente"}).SECRET_KEY == "valor-do-ambiente"
    assert Settings({}).SECRET_KEY != Settings({}).SECRET_KEY


def test_producao_exige_secret_key_e_proibe_debug():
    from config.settings import Settings

    with pytest.raises(RuntimeError):
        Settings({"APP_ENV": "production"})
    with pytest.raises(RuntimeError):
        Settings({"APP_ENV": "production", "SECRET_KEY": "x", "APP_DEBUG": "true"})


def test_fonte_sem_segredos_literais():
    assert "SECRET_KEY'] = '" not in (RAIZ / "app.py").read_text(encoding="utf-8")
    assert not (RAIZ / "services" / "notification_service.py").exists()


# ---------- F-005: hash de senha ----------

def test_senha_usa_kdf_com_salt():
    from models.user import User

    primeiro, segundo = User(), User()
    primeiro.set_password("segredo")
    segundo.set_password("segredo")
    assert primeiro.password != hashlib.md5(b"segredo").hexdigest()
    assert primeiro.password != segundo.password
    assert primeiro.check_password("segredo")
    assert not primeiro.check_password("errada")


def test_hash_md5_legado_migra_na_primeira_conferencia():
    from models.user import User

    usuario = User(password=hashlib.md5(b"segredo").hexdigest())
    assert not usuario.check_password("errada")
    assert usuario.password == hashlib.md5(b"segredo").hexdigest()
    assert usuario.check_password("segredo")
    assert usuario.password != hashlib.md5(b"segredo").hexdigest()
    assert usuario.check_password("segredo")


# ---------- F-002 e F-012: token e limite de login ----------

def test_token_assinado_valida_adulteracao_e_expiracao():
    from services.token_service import TokenService

    usuario = SimpleNamespace(id=7, password="hash-atual")
    carregar = {7: usuario}.get
    servico = TokenService("chave-a", 60)
    token = servico.issue(usuario)
    assert servico.verify(token, carregar) is usuario
    assert servico.verify(token + "x", carregar) is None
    assert TokenService("chave-b", 60).verify(token, carregar) is None
    assert TokenService("chave-a", -1).verify(token, carregar) is None


def test_token_vinculado_a_credencial_da_conta():
    from itsdangerous import URLSafeTimedSerializer

    from services.token_service import TokenService

    servico = TokenService("chave-a", 60)
    token = servico.issue(SimpleNamespace(id=7, password="hash-original"))
    assert servico.verify(token, {7: SimpleNamespace(id=7, password="hash-original")}.get).id == 7
    assert servico.verify(token, {7: SimpleNamespace(id=7, password="hash-apos-troca")}.get) is None
    assert servico.verify(token, {7: SimpleNamespace(id=7, password="hash-da-conta-nova")}.get) is None
    assert servico.verify(token, {}.get) is None
    payload = URLSafeTimedSerializer("chave-a", salt="auth-token").loads(token)
    assert "hash-original" not in str(payload)
    sem_impressao = URLSafeTimedSerializer("chave-a", salt="auth-token").dumps({"user_id": 7})
    assert servico.verify(sem_impressao, {7: SimpleNamespace(id=7, password="hash-original")}.get) is None


def test_limite_de_login_libera_apos_a_janela():
    from middleware.security import LoginThrottle

    agora = [0]
    limite = LoginThrottle(2, 60, clock=lambda: agora[0])
    limite.register_failure("chave")
    assert not limite.is_blocked("chave")
    limite.register_failure("chave")
    assert limite.is_blocked("chave")
    agora[0] = 61
    assert not limite.is_blocked("chave")


# ---------- F-010, F-011 e F-016: camadas ----------

def test_estatisticas_calculadas_no_service(app_memoria):
    from database import db
    from models.task import Task
    from services import task_service
    from utils.clock import utcnow

    ontem = utcnow() - timedelta(days=1)
    db.session.add_all([
        Task(title="Atrasada", status="pending", due_date=ontem),
        Task(title="Concluida", status="done", due_date=ontem),
    ])
    db.session.commit()

    stats = task_service.get_stats()
    assert (stats["total"], stats["pending"], stats["done"], stats["overdue"]) == (2, 1, 1, 1)
    assert stats["completion_rate"] == 50.0


def test_categorias_em_modulo_proprio(app_memoria):
    endpoints = {r.endpoint for r in app_memoria.url_map.iter_rules() if r.rule.startswith("/categories")}
    assert endpoints
    assert all(endpoint.startswith("categories.") for endpoint in endpoints)


def test_remover_categoria_preserva_task_sem_vinculo(app_memoria):
    from database import db
    from models.category import Category
    from models.task import Task
    from services import category_service

    categoria = Category(name="Temporaria")
    db.session.add(categoria)
    db.session.commit()
    task = Task(title="Vinculada", category_id=categoria.id)
    db.session.add(task)
    db.session.commit()

    category_service.delete_category(categoria.id)
    assert db.session.get(Task, task.id).category_id is None


# ---------- CT-09 (F-029): escopo das tasks e referências ----------

def test_escopo_de_tasks_por_perfil():
    from models.user import User

    assert User(id=3, role="user").task_scope() == 3
    assert User(id=3, role="manager").task_scope() is None
    assert User(id=3, role="admin").task_scope() is None


def test_estatisticas_respeitam_o_responsavel(app_memoria):
    from database import db
    from models.task import Task
    from models.user import User
    from services import task_service

    dono = User(name="Dono", email="dono@teste.com", password="x")
    outro = User(name="Outro", email="outro@teste.com", password="x")
    db.session.add_all([dono, outro])
    db.session.commit()
    db.session.add_all([Task(title="Minha", user_id=dono.id), Task(title="Alheia", user_id=outro.id)])
    db.session.commit()

    assert task_service.get_stats(dono.id)["total"] == 1
    assert task_service.get_stats()["total"] == 2


@pytest.mark.parametrize("valor", [[], {}, [1], {"a": 1}, True, 1.5, 10 ** 30, str(10 ** 30)])
@pytest.mark.parametrize("campo", ["user_id", "category_id"])
def test_referencia_invalida_e_rejeitada(campo, valor):
    from utils.errors import AppError
    from validators.task_validator import parse_new_task, parse_task_update

    for analisar, dados in ((parse_new_task, {"title": "Titulo valido", campo: valor}), (parse_task_update, {campo: valor})):
        with pytest.raises(AppError) as erro:
            analisar(dados)
        assert erro.value.status == 400


def test_referencia_numerica_em_texto_e_normalizada():
    from validators.task_validator import parse_task_update

    assert parse_task_update({"user_id": "5"})["user_id"] == 5


def test_id_fora_da_faixa_do_banco_nao_existe(app_memoria):
    from models.task import Task

    assert Task.find(10 ** 30) is None


def test_dependencias_diretas_fixadas_na_versao_instalada():
    from importlib.metadata import version

    declaradas = (RAIZ / "requirements.txt").read_text(encoding="utf-8").split()
    for pacote in ("sqlalchemy", "werkzeug", "itsdangerous"):
        assert f"{pacote}=={version(pacote)}" in declaradas


def test_contagens_por_status_e_atraso_respeitam_o_responsavel(app_memoria):
    from database import db
    from models.task import Task
    from models.user import User
    from services import task_service
    from utils.clock import utcnow

    dono = User(name="Dono", email="dono@teste.com", password="x")
    outro = User(name="Outro", email="outro@teste.com", password="x")
    db.session.add_all([dono, outro])
    db.session.commit()
    ontem = utcnow() - timedelta(days=1)
    db.session.add_all([
        Task(title="Pendente atrasada", status="pending", user_id=dono.id, due_date=ontem),
        Task(title="Em andamento", status="in_progress", user_id=dono.id),
        Task(title="Concluida", status="done", user_id=dono.id, due_date=ontem),
        Task(title="Cancelada", status="cancelled", user_id=dono.id),
        Task(title="Alheia atrasada 1", status="pending", user_id=outro.id, due_date=ontem),
        Task(title="Alheia atrasada 2", status="in_progress", user_id=outro.id, due_date=ontem),
        Task(title="Alheia concluida", status="done", user_id=outro.id),
    ])
    db.session.commit()

    assert task_service.get_stats(dono.id) == {
        "total": 4, "pending": 1, "in_progress": 1, "done": 1, "cancelled": 1,
        "overdue": 1, "completion_rate": 25.0,
    }
    geral = task_service.get_stats()
    assert (geral["pending"], geral["in_progress"], geral["done"], geral["overdue"]) == (2, 2, 2, 3)


@pytest.mark.parametrize("valor", [2.5, 2.0, True, False, "2", None])
def test_prioridade_aceita_somente_inteiro_na_faixa(valor):
    from utils.errors import AppError
    from validators.task_validator import parse_new_task, parse_task_update

    for analisar, dados in ((parse_new_task, {"title": "Titulo valido", "priority": valor}), (parse_task_update, {"priority": valor})):
        with pytest.raises(AppError) as erro:
            analisar(dados)
        assert erro.value.status == 400
    assert parse_task_update({"priority": 2})["priority"] == 2


def test_texto_com_surrogate_isolado_e_rejeitado():
    from utils.errors import AppError
    from validators.category_validator import parse_category_update
    from validators.task_validator import parse_new_task
    from validators.user_validator import parse_credentials

    for analisar, dados in ((parse_new_task, {"title": "abc\ud800"}), (parse_new_task, {"title": "Valido", "tags": ["\udfff"]}),
                            (parse_category_update, {"name": "\ud800"}), (parse_credentials, {"email": "a@b.com", "password": "\ud800x"})):
        with pytest.raises(AppError) as erro:
            analisar(dados)
        assert erro.value.status == 400


# ---------- CT-08 (F-018): limite padrão ----------

def test_listagem_limita_a_100_itens_por_padrao(app_memoria):
    from database import db
    from models.task import Task
    from models.user import User

    usuario = User(name="Leitor", email="leitor@teste.com")
    usuario.set_password("segredo")
    db.session.add(usuario)
    db.session.commit()
    db.session.add_all([Task(title=f"Task {n}", user_id=usuario.id) for n in range(101)])
    db.session.commit()

    token = app_memoria.extensions["token_service"].issue(usuario)
    cabecalho = {"Authorization": f"Bearer {token}"}
    cliente = app_memoria.test_client()
    assert len(cliente.get("/tasks", headers=cabecalho).get_json()) == 100
    assert len(cliente.get("/tasks?offset=100", headers=cabecalho).get_json()) == 1
