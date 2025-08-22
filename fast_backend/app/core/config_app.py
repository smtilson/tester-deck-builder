from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import AnyHttpUrl, EmailStr, HttpUrl, field_validator, model_validator

from pydantic_settings import BaseSettings, SettingsConfigDict

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
    model_config = SettingsConfigDict(
        env_file="fast_backend/.env", case_sensitive=True, extra="ignore"
    )

    @property
    def PATHS(self) -> Paths:
        return Paths()

    APP_NAME: str = "fast-backend"
    ENVIRONMENT: Environment = Environment.dev
    DEBUG: bool = True

    SECRET_KEY: str
    AUTH_TOKEN_LIFETIME_SECONDS: int = 3600

    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"  # type:ignore

    # --- MongoDB settings ---
    DATABASE_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "tester_deck_builder"

    # --- Sentry DSN ---
    SENTRY_DSN: HttpUrl | None = None

    PAGINATION_PER_PAGE: int = 20

    ADMIN_EMAIL: EmailStr = "seantilson@gmail.com"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before", check_fields=False)
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # --- Email/SES Settings ---
    SES_ACCESS_KEY: str | None = None
    SES_SECRET_KEY: str | None = None
    SES_REGION: str | None = None
    DEFAULT_FROM_EMAIL: EmailStr = "seantilson@gmail.com"
    DEFAULT_FROM_NAME: str | None = "Sean"
    EMAILS_ENABLED: bool = False
    # SMTP_HOST: str | None = None
    # SMTP_PORT: int | None = None

    @model_validator(mode="before")
    @classmethod
    def check_emails_enabled(cls, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(data, dict):
            access = bool(data.get("SES_ACCESS_KEY"))
            secret = bool(data.get("SES_SECRET_KEY"))
            region = bool(data.get("SES_REGION"))
            if access and secret and region:
                data["EMAILS_ENABLED"] = True
        return data

    FIRST_SUPERUSER_EMAIL: EmailStr = "seantilson@gmail.com"
    FIRST_SUPERUSER_PASSWORD: str

    """
    # this was not working since there is already a default value?
    @field_validator("EMAILS_ENABLED", mode="before")
    @classmethod
    def get_emails_enabled(cls, _: bool, values: dict[str, Any]) -> bool:
        return bool(
            values.get("SES_ACCESS_KEY")
            and values.get("SES_SECRET_KEY")
            and values.get("SES_REGION")
        )
    """


settings = Settings()
