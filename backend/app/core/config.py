from enum import Enum

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    development = "development"
    testing = "testing"
    production = "production"


class Settings(BaseSettings):
    APP_NAME: str = "LedgerAI"

    ENVIRONMENT: Environment = Environment.development

    DEBUG: bool = False

    DATABASE_URL: str

    REDIS_URL: str

    SECRET_KEY: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()