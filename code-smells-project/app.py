"""Composition root: cria a aplicação, injeta dependências e registra rotas e middlewares."""
import logging
import secrets

from flask import Flask
from flask_cors import CORS

from config.logging_config import configurar_logging
from config.settings import Settings
from database.connection import close_db, get_db
from database.schema import inicializar_banco
from middlewares.error_handler import registrar_tratadores_de_erro
from middlewares.security import registrar_protecoes_http
from routes import registrar_rotas
from services.container import Services

logger = logging.getLogger(__name__)


def create_app():
    configurar_logging(Settings.LOG_LEVEL)
    app = Flask(__name__)

    chave = Settings.SECRET_KEY
    if not chave:
        chave = secrets.token_hex(32)
        logger.warning("SECRET_KEY não definida: usando chave efêmera (tokens expiram ao reiniciar)")
    app.config.update(
        SECRET_KEY=chave,
        DEBUG=Settings.DEBUG,
        DB_PATH=Settings.DB_PATH,
        AMBIENTE=Settings.AMBIENTE,
        TOKEN_MAX_AGE_SEGUNDOS=Settings.TOKEN_MAX_AGE_SEGUNDOS,
    )

    CORS(app, origins=Settings.CORS_ORIGINS)
    inicializar_banco(app.config["DB_PATH"])
    app.teardown_appcontext(close_db)

    app.extensions["services"] = Services(get_db)
    registrar_protecoes_http(app, Settings.LOGIN_MAX_TENTATIVAS, Settings.LOGIN_JANELA_SEGUNDOS)
    registrar_tratadores_de_erro(app)
    registrar_rotas(app)
    return app


app = create_app()

if __name__ == "__main__":
    logger.info("Servidor iniciado em http://%s:%s", Settings.HOST, Settings.PORT)
    app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
