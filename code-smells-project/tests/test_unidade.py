"""Testes de prova (unidade/estrutura) das correções que não são observáveis só pela rota.

Cada teste cita o F-xxx/CT-xx do relatório reports/audit-project-1.md que comprova.
"""
import re
import sys
from pathlib import Path

import pytest

DIR_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DIR_PROJETO))

IGNORAR_DIRS = {"tests", ".venv", "venv", ".claude", "__pycache__", ".pytest_cache"}


def _fontes():
    return [p for p in DIR_PROJETO.rglob("*.py") if not (set(p.relative_to(DIR_PROJETO).parts) & IGNORAR_DIRS)]


def _settings(tmp_path, **extra):
    from config.settings import Settings
    return Settings({"DB_PATH": str(tmp_path / "unit.db"), **extra})


# ---------- F-001 / F-002: sem segredo, senha de seed ou debug fixos no código ----------

def test_f001_f002_codigo_sem_segredos_nem_debug_fixo():
    proibidos = [
        r"SECRET_KEY[\"']?\]?\s*=\s*[\"']",                      # chave atribuída como literal
        r"[\"']secret_key[\"']\s*:",                               # chave devolvida em resposta
        r"\(\s*\"[^\"]+\",\s*\"[^\"]+@[^\"]+\",\s*\"[^\"]+\",\s*\"(admin|cliente)\"\s*\)",  # seed com senha literal
        r"debug\s*=\s*True", r"[\"']0\.0\.0\.0[\"']", r"DEBUG[\"']\]\s*=\s*True",
    ]
    achados = [(p.name, padrao) for p in _fontes() for padrao in proibidos
               if re.search(padrao, p.read_text(encoding="utf-8"))]
    assert achados == []


def test_f001_f002_config_padrao_segura():
    from config.settings import Settings
    a, b = Settings({}), Settings({})
    assert a.DEBUG is False and a.HOST == "127.0.0.1"
    assert a.SEED_ADMIN_PASSWORD is None and a.SEED_CLIENTE_PASSWORD is None
    assert a.SECRET_KEY and a.SECRET_KEY != b.SECRET_KEY  # chave aleatória por processo, nunca literal
    assert Settings({"SECRET_KEY": "k" * 32}).SECRET_KEY == "k" * 32


# ---------- F-007: hash de senha e migração de senha legada ----------

class _UsuariosEmMemoria:
    def __init__(self):
        self.registros = {}

    def obter(self, usuario_id):
        return self.registros.get(usuario_id)

    def obter_por_email(self, email):
        return next((u for u in self.registros.values() if u["email"] == email), None)

    def criar(self, nome, email, senha_hash, tipo="cliente"):
        novo_id = len(self.registros) + 1
        self.registros[novo_id] = {"id": novo_id, "nome": nome, "email": email, "senha": senha_hash, "tipo": tipo}
        return novo_id

    def atualizar_senha(self, usuario_id, senha_hash):
        self.registros[usuario_id]["senha"] = senha_hash


def test_f007_cadastro_grava_hash_e_login_verifica():
    from services.usuario_service import UsuarioService
    repo = _UsuariosEmMemoria()
    servico = UsuarioService(repo)
    uid = servico.criar("Ana", "ana@x.com", "s3nha-forte")
    assert repo.registros[uid]["senha"].startswith(("scrypt:", "pbkdf2:"))
    assert servico.autenticar("ana@x.com", "s3nha-forte")["id"] == uid
    assert servico.autenticar("ana@x.com", "errada") is None


def test_f007_senha_legada_em_texto_e_migrada_no_login():
    from services.usuario_service import UsuarioService
    repo = _UsuariosEmMemoria()
    repo.registros[1] = {"id": 1, "nome": "Legado", "email": "leg@x.com", "senha": "antiga", "tipo": "cliente"}
    servico = UsuarioService(repo)
    assert servico.autenticar("leg@x.com", "errada") is None
    assert repo.registros[1]["senha"] == "antiga"
    assert servico.autenticar("leg@x.com", "antiga")["id"] == 1
    assert repo.registros[1]["senha"].startswith(("scrypt:", "pbkdf2:"))


# ---------- CT-07: token assinado ----------

def test_ct07_token_assinado_e_verificado():
    from services.auth_service import TokenService
    servico = TokenService("chave-de-teste", 60)
    token = servico.emitir({"id": 7, "tipo": "admin"})
    assert servico.verificar(token) == {"id": 7, "tipo": "admin"}
    assert servico.verificar(token + "x") is None
    assert TokenService("outra-chave", 60).verificar(token) is None


# ---------- F-012: transação na criação do pedido ----------

def _banco_com_dados(tmp_path):
    from database.connection import conectar
    from database.schema import inicializar_banco
    settings = _settings(tmp_path)
    inicializar_banco(settings)
    conexao = conectar(settings.DB_PATH)
    with conexao:
        conexao.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES ('U', 'u@x.com', 'h', 'cliente')")
    return conexao


def test_f012_falha_no_meio_desfaz_baixa_de_estoque(tmp_path):
    from models.pedido_model import EstoqueInsuficiente, PedidoModel, ProdutoInexistente
    from services.pedido_service import calcular_total
    conexao = _banco_com_dados(tmp_path)
    modelo = PedidoModel(lambda: conexao)
    estoque = lambda pid: conexao.execute("SELECT estoque FROM produtos WHERE id = ?", (pid,)).fetchone()[0]

    with pytest.raises(ProdutoInexistente):
        modelo.criar(1, [{"produto_id": 1, "quantidade": 2}, {"produto_id": 9999, "quantidade": 1}], calcular_total)
    with pytest.raises(EstoqueInsuficiente):
        modelo.criar(1, [{"produto_id": 1, "quantidade": 2}, {"produto_id": 6, "quantidade": 999}], calcular_total)
    assert estoque(1) == 10 and estoque(6) == 8
    assert conexao.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0] == 0
    assert conexao.execute("SELECT COUNT(*) FROM itens_pedido").fetchone()[0] == 0

    modelo.criar(1, [{"produto_id": 6, "quantidade": 8}], calcular_total)
    with pytest.raises(EstoqueInsuficiente):  # baixa condicional: não vende além do estoque
        modelo.criar(1, [{"produto_id": 6, "quantidade": 1}], calcular_total)
    assert estoque(6) == 0
    conexao.close()


# ---------- F-014: regra de negócio isolada em services (testável sem HTTP/banco) ----------

def test_f014_regras_testaveis_sem_http():
    from decimal import Decimal

    from services.erros import AppError
    from services.pedido_service import PedidoService, calcular_total
    from services.relatorio_service import calcular_desconto

    assert calcular_desconto(20000) == Decimal("2000.00")
    assert calcular_desconto(6000) == Decimal("300.00")
    assert calcular_desconto(2000) == Decimal("40.00")
    assert calcular_desconto(1000) == 0
    assert calcular_total([(0.1, 3), (0.2, 1)]) == 0.5

    class _SemUsuario:
        def existe(self, _):
            return False

    with pytest.raises(AppError) as erro:
        PedidoService(pedido_model=None, usuario_service=_SemUsuario()).criar(1, [{"produto_id": 1, "quantidade": 1}])
    assert erro.value.status == 400


# ---------- F-015: sem conexão global compartilhada ----------

def test_f015_apps_nao_compartilham_conexao(tmp_path):
    import database.connection as conexao_mod
    from app import create_app
    assert not any(isinstance(v, __import__("sqlite3").Connection) for v in vars(conexao_mod).values())
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    app_a = create_app(_settings(tmp_path / "a"))
    app_b = create_app(_settings(tmp_path / "b"))
    with app_a.app_context():
        app_a.extensions["loja"].produto_service.criar(
            {"nome": "Só em A", "descricao": "", "preco": 1, "estoque": 1, "categoria": "geral"})
        em_a = app_a.extensions["loja"].sistema_service.contagens()["produtos"]
    with app_b.app_context():
        em_b = app_b.extensions["loja"].sistema_service.contagens()["produtos"]
    assert (em_a, em_b) == (11, 10)


# ---------- F-009 / F-013: camadas separadas; sem SQL fora da camada de dados ----------

def test_f009_f013_sem_sql_fora_da_camada_de_dados():
    camadas_http = [p for p in _fontes() if p.parts[-2] in ("controllers", "routes", "views", "middlewares")]
    camadas_http.append(DIR_PROJETO / "app.py")
    assert len(camadas_http) >= 8
    for arquivo in camadas_http:
        codigo = arquivo.read_text(encoding="utf-8")
        assert "sqlite3" not in codigo and ".execute(" not in codigo, arquivo.name
        assert not re.search(r"\b(SELECT|INSERT|UPDATE|DELETE)\b\s", codigo), arquivo.name
    for pacote in ("config", "models", "services", "controllers", "routes", "views", "middlewares", "database"):
        assert (DIR_PROJETO / pacote).is_dir(), pacote
