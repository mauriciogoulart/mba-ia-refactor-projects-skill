"""Configuração da aplicação lida do ambiente (nenhum segredo literal no código)."""
import os
import secrets


class Settings:
    def __init__(self, env=None):
        env = os.environ if env is None else env
        chave = env.get("SECRET_KEY")
        # Sem SECRET_KEY definida, gera uma chave aleatória por processo (tokens expiram ao reiniciar).
        self.SECRET_KEY = chave or secrets.token_hex(32)
        self.SECRET_KEY_GERADA = not chave
        self.DEBUG = env.get("APP_DEBUG", "false").lower() == "true"
        self.HOST = env.get("APP_HOST", "127.0.0.1")
        self.PORT = int(env.get("APP_PORT", "5000"))
        self.AMBIENTE = env.get("APP_ENV", "producao")
        self.DB_PATH = env.get("DB_PATH", "loja.db")
        self.CORS_ORIGINS = [o.strip() for o in env.get("CORS_ORIGINS", "").split(",") if o.strip()]
        # Senhas dos usuários de demonstração: sem valor padrão; sem a variável, o usuário não é semeado.
        self.SEED_ADMIN_PASSWORD = env.get("SEED_ADMIN_PASSWORD")
        self.SEED_CLIENTE_PASSWORD = env.get("SEED_CLIENTE_PASSWORD")
        self.TOKEN_MAX_AGE = int(env.get("TOKEN_MAX_AGE", "3600"))
        self.LOGIN_MAX_TENTATIVAS = int(env.get("LOGIN_MAX_TENTATIVAS", "5"))
        self.LOGIN_JANELA_SEGUNDOS = int(env.get("LOGIN_JANELA_SEGUNDOS", "300"))
