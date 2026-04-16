"""Centralized settings loaded from `.env` (local dev) or env vars (production).

In local dev, `.env` sits at the monorepo root. In Docker/Railway there's no
`.env` file and environment variables are injected directly — pydantic-settings
handles both transparently as long as we don't crash when `.env` is missing.
"""
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> Path | None:
    """Walk up from this file looking for the first `.env`. Returns None in prod."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / ".env"
        if candidate.exists():
            return candidate
    return None


_ENV_FILE = _find_env_file()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    secret_key: str = Field(default="dev-secret-change-me")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://trendradar:trendradar@localhost:5432/trendradar"
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # LLM — DeepSeek (OpenAI-compatible API)
    deepseek_api_key: str = Field(default="")
    deepseek_base_url: str = Field(default="https://api.deepseek.com/v1")

    # LLM — Anthropic
    anthropic_api_key: str = Field(default="")

    # Model routing by user plan
    llm_free_tier_model: str = Field(default="deepseek-chat")
    llm_pro_tier_model: str = Field(default="claude-sonnet-4-6")

    # Prod domains (comma-separated) allowed to hit the API. e.g.
    #   CORS_ORIGINS="https://trendradar.ai,https://www.trendradar.ai"
    # Vercel preview URLs (*.vercel.app) are matched by a regex in main.py.
    cors_origins: str = Field(default="")

    @property
    def is_dev(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Cached factory. Safe to call from anywhere; instantiation happens once."""
    return Settings()
