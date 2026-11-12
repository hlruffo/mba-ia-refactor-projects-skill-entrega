"""Configuração da aplicação carregada a partir do ambiente.

Nenhum segredo é escrito neste arquivo. Veja `.env.example` para as chaves
suportadas.
"""

import logging
import os
import secrets

LOGGER = logging.getLogger(__name__)

APP_VERSION = "1.0.0"

_TRUE_VALUES = {"1", "true", "t", "yes", "y", "on"}


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in _TRUE_VALUES


def _as_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class Config:
    """Valores de configuração com defaults seguros."""

    def __init__(self, env=None, **overrides):
        env = os.environ if env is None else env

        self.ENVIRONMENT = env.get("APP_ENV", "development")
        self.DEBUG = _as_bool(env.get("FLASK_DEBUG"), default=False)
        self.APP_VERSION = APP_VERSION

        self.DATABASE_PATH = env.get("DATABASE_PATH", "loja.db")
        self.AUTO_INIT_DB = _as_bool(env.get("AUTO_INIT_DB"), default=True)

        self.HOST = env.get("HOST", "127.0.0.1")
        self.PORT = _as_int(env.get("PORT"), 5000)

        # Lista separada por vírgula. Vazio = CORS desabilitado.
        origins = env.get("CORS_ORIGINS", "")
        self.CORS_ORIGINS = [o.strip() for o in origins.split(",") if o.strip()]

        # Endpoints administrativos ficam desligados a menos que habilitados
        # explicitamente E com token definido.
        self.ADMIN_API_ENABLED = _as_bool(env.get("ADMIN_API_ENABLED"), default=False)
        self.ADMIN_API_TOKEN = env.get("ADMIN_API_TOKEN") or ""

        self.LOG_LEVEL = env.get("LOG_LEVEL", "INFO")

        self.SECRET_KEY = self._resolve_secret_key(env)

        for key, value in overrides.items():
            setattr(self, key, value)

        self._validate()

    def _resolve_secret_key(self, env):
        secret = env.get("SECRET_KEY")
        if secret:
            return secret
        if self.ENVIRONMENT == "production":
            raise RuntimeError(
                "SECRET_KEY é obrigatório quando APP_ENV=production. "
                "Defina a variável de ambiente antes de iniciar a aplicação."
            )
        LOGGER.warning(
            "SECRET_KEY ausente; gerando chave efêmera para o ambiente '%s'. "
            "Sessões não sobrevivem a um restart.",
            self.ENVIRONMENT,
        )
        return secrets.token_urlsafe(32)

    def _validate(self):
        if self.ADMIN_API_ENABLED and not self.ADMIN_API_TOKEN:
            raise RuntimeError("ADMIN_API_ENABLED=true exige ADMIN_API_TOKEN definido.")
        if self.ENVIRONMENT == "production" and self.DEBUG:
            raise RuntimeError("FLASK_DEBUG não pode ser true em produção.")

    def as_flask_mapping(self):
        """Somente o que o Flask precisa conhecer."""
        return {
            "SECRET_KEY": self.SECRET_KEY,
            "DEBUG": self.DEBUG,
            "DATABASE_PATH": self.DATABASE_PATH,
            "APP_VERSION": self.APP_VERSION,
            "ENVIRONMENT": self.ENVIRONMENT,
            "ADMIN_API_ENABLED": self.ADMIN_API_ENABLED,
            "ADMIN_API_TOKEN": self.ADMIN_API_TOKEN,
        }
