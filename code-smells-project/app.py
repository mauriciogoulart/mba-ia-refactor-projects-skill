"""Composition root: cria a aplicação, injeta dependências, registra rotas e middlewares."""
import logging
from types import SimpleNamespace

from flask import Flask

from config.logging_config import configurar_logging
from config.settings import Settings
from database import connection
from database.schema import inicializar_banco
from middlewares.errors import registrar_handlers_de_erro
from middlewares.security import LimitadorDeLogin, registrar_protecoes_http
from models.admin_model import AdminModel
from models.pedido_model import PedidoModel
from models.produto_model import ProdutoModel
from models.usuario_model import UsuarioModel
from routes import registrar_rotas
from services.auth_service import TokenService
from services.pedido_service import PedidoService
from services.produto_service import ProdutoService
from services.relatorio_service import RelatorioService
from services.sistema_service import SistemaService
from services.usuario_service import UsuarioService

logger = logging.getLogger(__name__)


def create_app(settings=None):
    settings = settings or Settings()
    configurar_logging(settings.DEBUG)
    if settings.SECRET_KEY_GERADA:
        logger.warning("SECRET_KEY não definida: usando chave aleatória deste processo (tokens não sobrevivem a reinícios)")

    app = Flask(__name__)
    app.config.update(SECRET_KEY=settings.SECRET_KEY, DEBUG=settings.DEBUG,
                      DB_PATH=settings.DB_PATH, AMBIENTE=settings.AMBIENTE)

    inicializar_banco(settings)
    connection.init_app(app)

    obter_conexao = connection.obter_conexao
    produto_model = ProdutoModel(obter_conexao)
    usuario_model = UsuarioModel(obter_conexao)
    pedido_model = PedidoModel(obter_conexao)
    usuario_service = UsuarioService(usuario_model)
    app.extensions["loja"] = SimpleNamespace(
        produto_service=ProdutoService(produto_model),
        usuario_service=usuario_service,
        pedido_service=PedidoService(pedido_model, usuario_service),
        relatorio_service=RelatorioService(pedido_model),
        sistema_service=SistemaService(produto_model, usuario_model, pedido_model, AdminModel(obter_conexao)),
        token_service=TokenService(settings.SECRET_KEY, settings.TOKEN_MAX_AGE),
        limitador_login=LimitadorDeLogin(settings.LOGIN_MAX_TENTATIVAS, settings.LOGIN_JANELA_SEGUNDOS),
    )

    registrar_protecoes_http(app, settings)
    registrar_handlers_de_erro(app)
    registrar_rotas(app)
    return app


if __name__ == "__main__":
    configuracao = Settings()
    aplicacao = create_app(configuracao)
    logger.info("Servidor iniciado em http://%s:%s", configuracao.HOST, configuracao.PORT)
    aplicacao.run(host=configuracao.HOST, port=configuracao.PORT, debug=configuracao.DEBUG)
