"""FastAPI application entry point.

Run locally:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Docs at:
    http://localhost:8000/docs   (Swagger UI)
    http://localhost:8000/redoc  (ReDoc)
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1 import api_router
from app.core.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="TrendRadar API",
    version=__version__,
    description="AI product-research agent for TikTok Shop US sellers.",
    docs_url="/docs" if settings.is_dev else None,  # disable in prod
    redoc_url="/redoc" if settings.is_dev else None,
)

# CORS — dev origins by default; add prod URLs via CORS_ORIGINS env var (comma-separated).
_default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
_extra = [o.strip() for o in (settings.cors_origins or "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_default_origins + _extra,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Vercel preview deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root() -> dict:
    return {
        "service": "trendradar-api",
        "version": __version__,
        "docs": "/docs",
    }


@app.on_event("startup")
async def startup() -> None:
    logger.info("TrendRadar API v%s starting in %s mode", __version__, settings.app_env)


@app.on_event("shutdown")
async def shutdown() -> None:
    logger.info("TrendRadar API shutting down")
