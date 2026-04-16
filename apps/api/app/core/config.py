"""Centralized settings loaded from `.env`.

Everything that reads env vars goes through `get_settings()` — never call `os.environ`
directly in the app code. This keeps typing tight and lets us swap config sources later.
"""
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Monorepo root — .env lives here.
#   app/core/config.py → app/core → app → apps/api → apps → trendradar-app
ROOT_DIR = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
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
