from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import (
    AnyHttpUrl,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    validator,
)

from pydantic_settings import BaseSettings

try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):
        pass


class Environment(StrEnum):
    dev = "dev"
    prod = "prod"


class Paths:
    # fast_backend
    ROOT_DIR: Path = Path(__file__).parent.parent.parent
    BASE_DIR: Path = ROOT_DIR / "app"
    EMAIL_TEMPLATES_DIR: Path = BASE_DIR / "emails"
    LOGIN_PATH: str = "/auth/login"


class Settings(BaseSettings):
    @property
    def PATHS(self) -> Paths:
        return Paths()

    APP_NAME: str = "test"
    DEBUG: bool = True
    ADMIN_EMAIL: str = "seantilson@gmail.com"
    DATABASE_URI: str = "postgres://s_user:yadda@localhost:5432/tester_deck_builder"
    DEFAULT_FROM_EMAIL: EmailStr = "seantilson@gmail.com"
    DEFAULT_FROM_NAME: str | None = None

    @validator("DATABASE_URI")
    def assemble_db_connection(cls, v: Any) -> str:
        if isinstance(v, str):
            return v
        return str(v)

    class Config:
        env_file = ".env"
        case_sensitive = True


class PreSettings(BaseSettings):
    @property
    def PATHS(self) -> Paths:
        return Paths()

    ENVIRONMENT: Environment = "dev"
    SECRET_KEY: str = "yadda"
    DEBUG: bool = True
    AUTH_TOKEN_LIFETIME_SECONDS: int = 3600
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"  # type:ignore
    SENTRY_DSN: HttpUrl | None = None
    PAGINATION_PER_PAGE: int = 20
    ADMIN_EMAIL: str = "seantilson@gmail.com"
    DATABASE_URI: str = "postgres://s_user:yadda@localhost:5432/tester_deck_builder"

    REDIS_URL: str = "redis://dummy"

    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    DATABASE_URI: str = "postgres://s_user:yadda@localhost:5432/tester_deck_builder"

    SES_ACCESS_KEY: str | None = None
    SES_SECRET_KEY: str | None = None
    SES_REGION: str | None = None
    DEFAULT_FROM_EMAIL: EmailStr = "seantilson@gmail.com"
    DEFAULT_FROM_NAME: str | None = None
    EMAILS_ENABLED: bool = True #False true put in for testing purposes?

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, _: bool, values: dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("DEFAULT_FROM_EMAIL")
        )

    FIRST_SUPERUSER_EMAIL: EmailStr = "seantilson@gmail.com"
    FIRST_SUPERUSER_PASSWORD: str = "yadda"

    class Config:
        env_file = ".env"


settings = PreSettings()
