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
    OPENAI_API_KEY: SecretStr
    OPENAI_MODEL: str = "gpt-5"
    OPENAI_TEMPERATURE: float = 0.2
    OPENAI_MAX_TOKENS: int = 2000

    # JWT Configuration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()