"""Liveness + readiness checks. Use `/api/v1/health` for monitoring."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    """Liveness — app is running."""
    return {"status": "ok", "env": get_settings().app_env}


@router.get("/health/ready")
async def ready(session: AsyncSession = Depends(get_session)) -> dict:
    """Readiness — dependencies are reachable."""
    await session.execute(text("SELECT 1"))
    return {"status": "ready", "db": "ok"}
