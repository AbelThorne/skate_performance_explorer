import os
import secrets
from typing import Literal

from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    PROJECT_NAME: str = (
        f"Skate Performance Explorer - {os.getenv('ENV', 'development').capitalize()}"
    )
    DESCRIPTION: str = (
        "An application to explore and analyse figure skating performances"
    )
    ENV: Literal["development", "staging", "production"] = "development"
    VERSION: str = "0.1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    DATABASE_URI: str = "postgresql+psycopg2://skating:skating@localhost:5432/skating"
    API_USERNAME: str = "skating"
    API_PASSWORD: str = "skating"

    class Config:
        case_sensitive = True


settings = Settings()


class TestSettings(Settings):
    class Config:
        case_sensitive = True


test_settings = TestSettings()
