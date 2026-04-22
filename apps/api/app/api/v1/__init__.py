"""v1 API router — mounts all sub-routers under /api/v1."""
from fastapi import APIRouter

from app.api.v1 import chat, health, waitlist

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(waitlist.router, tags=["waitlist"])
