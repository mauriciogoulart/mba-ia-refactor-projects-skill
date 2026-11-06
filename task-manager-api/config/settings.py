"""Configuração da aplicação lida exclusivamente de variáveis de ambiente."""
import os
import secrets
from dataclasses import dataclass, field


def _env_bool(name, default="false"):
    return os.environ.get(name, default).strip().lower() == "true"


def _env_list(name):
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    SECRET_KEY: str
    SECRET_KEY_FROM_ENV: bool
    DEBUG: bool = False
    HOST: str = "127.0.0.1"
    PORT: int = 5000
    DATABASE_URL: str = "sqlite:///tasks.db"
    CORS_ORIGINS: list = field(default_factory=list)
    TOKEN_MAX_AGE: int = 8 * 60 * 60
    LOG_LEVEL: str = "INFO"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SEED_ADMIN_PASSWORD: str | None = None
    SEED_MANAGER_PASSWORD: str | None = None
    SEED_USER_PASSWORD: str | None = None

    @classmethod
    def from_env(cls):
        secret_key = os.environ.get("SECRET_KEY")
        return cls(
            # Sem SECRET_KEY definida, gera uma chave aleatória por processo (tokens expiram a cada reinício).
            SECRET_KEY=secret_key or secrets.token_hex(32),
            SECRET_KEY_FROM_ENV=bool(secret_key),
            DEBUG=_env_bool("APP_DEBUG"),
            HOST=os.environ.get("APP_HOST", "127.0.0.1"),
            PORT=int(os.environ.get("APP_PORT", "5000")),
            DATABASE_URL=os.environ.get("DATABASE_URL", "sqlite:///tasks.db"),
            CORS_ORIGINS=_env_list("CORS_ORIGINS"),
            TOKEN_MAX_AGE=int(os.environ.get("TOKEN_MAX_AGE", str(8 * 60 * 60))),
            LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"),
            SMTP_HOST=os.environ.get("SMTP_HOST", "smtp.gmail.com"),
            SMTP_PORT=int(os.environ.get("SMTP_PORT", "587")),
            SMTP_USER=os.environ.get("SMTP_USER"),
            SMTP_PASSWORD=os.environ.get("SMTP_PASSWORD"),
            SEED_ADMIN_PASSWORD=os.environ.get("SEED_ADMIN_PASSWORD"),
            SEED_MANAGER_PASSWORD=os.environ.get("SEED_MANAGER_PASSWORD"),
            SEED_USER_PASSWORD=os.environ.get("SEED_USER_PASSWORD"),
        )
