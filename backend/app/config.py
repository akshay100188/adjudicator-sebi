"""Pydantic settings. Loads backend/.env."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_PATH, extra="ignore")

    supabase_url: str = ""
    supabase_service_key: str = ""
    database_url: str = ""
    db_schema: str = "adjudicator"
    environment: str = "development"

    # LLM keys (Phase 2 onward)
    anthropic_api_key: str = ""
    openai_api_key: str = ""


settings = Settings()
