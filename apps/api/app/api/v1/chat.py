"""Conversational pick endpoint.

POST /api/v1/chat/query
  Body: { "query": "给我 3 个美区家居爆品", "session_id": null }
  Returns: Server-Sent Events stream.

For MVP week 1, we:
  1. Pull 50 candidate products via a simple SQL query (mocked if DB empty)
  2. Build the picker prompt
  3. Stream LLM output back to the client

Authentication + session persistence come week 2.
"""
from __future__ import annotations

import json
from collections.abc import AsyncIterator
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.llm_router import LLMMessage
from app.core.llm_router import router as llm
from app.models.product import Product
from app.prompts.picker import build_picker_messages
from app.schemas.chat import ChatQueryRequest

router = APIRouter(prefix="/chat")
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# Placeholder mock candidates — used when DB is empty in very early dev.
# Replace once the scraper populates `products` table.
_MOCK_CANDIDATES = [
    {
        "product_id": "mock_led_nightlight",
        "title": "LED 便携小夜灯（触控款）",
        "price_usd": 19.99,
        "category": "Home",
        "gmv_14d": 58600,
        "growth_14d": 342,
        "shop_count": 23,
        "creator_count": 47,
        "review_count": 2180,
        "avg_rating": 4.6,
    },
    {
        "product_id": "mock_humidifier",
        "title": "静音加湿器 300ml",
        "price_usd": 24.99,
        "category": "Home",
        "gmv_14d": 42100,
        "growth_14d": 218,
        "shop_count": 41,
        "creator_count": 32,
        "review_count": 1560,
        "avg_rating": 4.5,
    },
    {
        "product_id": "mock_storage_basket",
        "title": "可折叠收纳篮（3 件套）",
        "price_usd": 15.99,
        "category": "Home",
        "gmv_14d": 35200,
        "growth_14d": 185,
        "shop_count": 18,
        "creator_count": 25,
        "review_count": 980,
        "avg_rating": 4.7,
    },
]


async def _candidates_for(query: str, session: AsyncSession) -> list[dict]:
    """Pre-filter 50 products from DB. Falls back to mock if DB is empty.

    Spreads raw JSONB fields (shop_count, creator_count, review_count, avg_rating, tags)
    into the candidate dict so the LLM has rich context to reason about competition
    intensity and creator momentum.
    """
    stmt = select(Product).order_by(Product.growth_14d.desc().nullslast()).limit(50)
    rows = (await session.execute(stmt)).scalars().all()
    if not rows:
        return _MOCK_CANDIDATES
    return [
        {
            "product_id": p.platform_id,  # use stable scraper-side id
            "title": p.title,
            "price_usd": float(p.price_usd) if p.price_usd else None,
            "category": p.category,
            "gmv_14d": float(p.gmv_14d) if p.gmv_14d else None,
            "growth_14d": float(p.growth_14d) if p.growth_14d else None,
            **(p.raw or {}),  # shop_count, creator_count, review_count, avg_rating, tags
        }
        for p in rows
    ]


@router.post("/query")
async def chat_query(
    req: ChatQueryRequest,
    session: SessionDep,
) -> StreamingResponse:
    """Stream a picking response as SSE.

    Client consumption (JS):
        const res = await fetch('/api/v1/chat/query', { method: 'POST', ... });
        const reader = res.body.getReader();
        // ... read chunks, each is a line "data: ...\\n\\n"
    """
    candidates = await _candidates_for(req.query, session)
    if not candidates:
        raise HTTPException(status_code=503, detail="No candidates available")

    messages = build_picker_messages(
        query=req.query,
        candidates_json=json.dumps(candidates, ensure_ascii=False),
        date=date.today().isoformat(),
    )
    llm_messages = [LLMMessage(**m) for m in messages]

    async def event_stream() -> AsyncIterator[bytes]:
        # First event: metadata
        yield _sse({"event": "start", "model": llm.pick_model("free")})
        try:
            async for chunk in llm.stream(llm_messages, plan="free"):
                yield _sse({"event": "delta", "text": chunk})
            yield _sse({"event": "done"})
        except Exception as e:
            yield _sse({"event": "error", "message": str(e)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _sse(payload: dict) -> bytes:
    """Format as a Server-Sent Event frame."""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode()
