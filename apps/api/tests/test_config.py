"""Settings validation tests."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_development_allows_local_database_default():
    settings = Settings(app_env="development")
    assert "localhost" in settings.database_url


def test_production_rejects_localhost_database_url():
    with pytest.raises(ValidationError, match="refusing to use localhost"):
        Settings(app_env="production")


def test_production_requires_asyncpg_database_url():
    with pytest.raises(ValidationError, match="postgresql\\+asyncpg"):
        Settings(
            app_env="production",
            database_url="postgresql://user:password@example.com/db?sslmode=require",
        )


def test_production_accepts_asyncpg_database_url():
    settings = Settings(
        app_env="production",
        database_url="postgresql+asyncpg://user:password@example.com/db?ssl=require",
    )
    assert settings.database_url.startswith("postgresql+asyncpg://")
