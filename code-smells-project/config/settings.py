"""Configuração da aplicação, lida exclusivamente de variáveis de ambiente."""
import os


def _ler_bool(nome, padrao=False):
    valor = os.environ.get(nome)
    if valor is None:
        return padrao
    return valor.strip().lower() in ("1", "true", "yes", "sim")


def _ler_lista(nome, padrao):
    valor = os.environ.get(nome, padrao)
    return [item.strip() for item in valor.split(",") if item.strip()]


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DEBUG = _ler_bool("APP_DEBUG", False)
    HOST = os.environ.get("APP_HOST", "127.0.0.1")
    PORT = int(os.environ.get("APP_PORT", "5000"))
    AMBIENTE = os.environ.get("APP_ENV", "producao")
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    TOKEN_MAX_AGE_SEGUNDOS = int(os.environ.get("TOKEN_MAX_AGE_SEGUNDOS", "28800"))
    CORS_ORIGINS = _ler_lista("CORS_ORIGINS", "*")
    LOGIN_MAX_TENTATIVAS = int(os.environ.get("LOGIN_MAX_TENTATIVAS", "10"))
    LOGIN_JANELA_SEGUNDOS = int(os.environ.get("LOGIN_JANELA_SEGUNDOS", "60"))
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
