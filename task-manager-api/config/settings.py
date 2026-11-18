"""Configuração da aplicação, lida exclusivamente do ambiente."""
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

ARQUIVO_ENV = Path(__file__).resolve().parent.parent / '.env'
VALORES_VERDADEIROS = {'1', 'true', 'yes', 'on'}


class Settings:
    def __init__(self, env):
        self.APP_ENV = env.get('APP_ENV', 'development').strip().lower()
        self.DEBUG = env.get('APP_DEBUG', 'false').strip().lower() in VALORES_VERDADEIROS
        self.HOST = env.get('APP_HOST', '127.0.0.1')
        self.PORT = int(env.get('APP_PORT', '5000'))
        self.DATABASE_URL = env.get('DATABASE_URL', 'sqlite:///tasks.db')
        self.LOG_LEVEL = env.get('LOG_LEVEL', 'INFO').upper()
        self.CORS_ORIGINS = [o.strip() for o in env.get('CORS_ORIGINS', '').split(',') if o.strip()]
        self.TOKEN_MAX_AGE_SECONDS = int(env.get('TOKEN_MAX_AGE_SECONDS', '3600'))
        self.LOGIN_MAX_FAILURES = int(env.get('LOGIN_MAX_FAILURES', '5'))
        self.LOGIN_WINDOW_SECONDS = int(env.get('LOGIN_WINDOW_SECONDS', '300'))
        self.SEED_ADMIN_PASSWORD = env.get('SEED_ADMIN_PASSWORD')
        self.SEED_USER_PASSWORD = env.get('SEED_USER_PASSWORD')
        self.SEED_MANAGER_PASSWORD = env.get('SEED_MANAGER_PASSWORD')

        chave = env.get('SECRET_KEY', '').strip()
        if self.APP_ENV == 'production':
            if not chave:
                raise RuntimeError('SECRET_KEY é obrigatória com APP_ENV=production')
            if self.DEBUG:
                raise RuntimeError('APP_DEBUG não pode ser ativado com APP_ENV=production')
        # Sem chave fora de produção, usa uma chave efêmera: os tokens expiram ao reiniciar.
        self.SECRET_KEY = chave or secrets.token_hex(32)


def load_settings():
    load_dotenv(ARQUIVO_ENV)
    return Settings(os.environ)
