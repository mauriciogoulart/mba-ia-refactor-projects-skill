"""Provas de unidade das correções (configuração, senha, token, services e estrutura)."""
import hashlib
from datetime import timedelta
from pathlib import Path

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

    servico = TokenService("chave-a", 60)
    token = servico.issue(7)
    assert servico.verify(token) == 7
    assert servico.verify(token + "x") is None
    assert TokenService("chave-b", 60).verify(token) is None
    assert TokenService("chave-a", -1).verify(token) is None


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


# ---------- CT-08 (F-018): limite padrão ----------

def test_listagem_limita_a_100_itens_por_padrao(app_memoria):
    from database import db
    from models.task import Task
    from models.user import User

    usuario = User(name="Leitor", email="leitor@teste.com")
    usuario.set_password("segredo")
    db.session.add(usuario)
    db.session.add_all([Task(title=f"Task {n}") for n in range(101)])
    db.session.commit()

    token = app_memoria.extensions["token_service"].issue(usuario.id)
    cabecalho = {"Authorization": f"Bearer {token}"}
    cliente = app_memoria.test_client()
    assert len(cliente.get("/tasks", headers=cabecalho).get_json()) == 100
    assert len(cliente.get("/tasks?offset=100", headers=cabecalho).get_json()) == 1
