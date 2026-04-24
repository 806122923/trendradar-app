"""Waitlist endpoints.

Two ingress paths:
  1. POST /api/v1/waitlist           · direct submit from landing page JS
  2. POST /api/v1/waitlist/tally     · Tally.so webhook (HMAC-signed)

Both paths funnel into the same service function so business logic stays single-sourced.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.integrations.email_templates import welcome_email
from app.integrations.resend_client import send_email
from app.models.waitlist import WaitlistEntry
from app.schemas.waitlist import (
    WaitlistJoinRequest,
    WaitlistJoinResponse,
    WaitlistStats,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/waitlist")
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# ---------------------------------------------------------------------------
# Core service function
# ---------------------------------------------------------------------------

async def _join_waitlist(
    *, req: WaitlistJoinRequest, session: AsyncSession
) -> WaitlistJoinResponse:
    """Idempotent: if the email is already on the list, return the existing record.

    Returns the position (Nth to join) so the frontend can render
    "You're #247 — locked in" without a second round-trip.
    """
    # Case-insensitive lookup — users sometimes re-submit with different casing
    existing_stmt = select(WaitlistEntry).where(
        func.lower(WaitlistEntry.email) == req.email.lower()
    )
    existing = (await session.execute(existing_stmt)).scalar_one_or_none()
    if existing:
        return WaitlistJoinResponse(
            id=existing.id,
            email=existing.email,
            position=existing.position,
            created_at=existing.created_at,
            already_registered=True,
        )

    # Position = (count + 1). Using COUNT is fine at our scale (<100k rows).
    count_stmt = select(func.count()).select_from(WaitlistEntry)
    current_count = (await session.execute(count_stmt)).scalar_one()
    next_position = int(current_count) + 1

    entry = WaitlistEntry(
        email=req.email.lower(),
        position=next_position,
        source=req.source,
        referrer=req.referrer,
        metadata_json=req.metadata,
    )
    session.add(entry)
    # Flush to get the id + created_at, commit happens at request end via get_session
    await session.flush()
    await session.refresh(entry)

    # Fire-and-forget welcome email — don't let email failure block signup
    await _try_send_welcome_email(entry, session=session)

    logger.info("✅ Waitlist join email=%s position=%d", entry.email, entry.position)

    return WaitlistJoinResponse(
        id=entry.id,
        email=entry.email,
        position=entry.position,
        created_at=entry.created_at,
        already_registered=False,
    )


async def _try_send_welcome_email(entry: WaitlistEntry, *, session: AsyncSession) -> None:
    """Best-effort send. Updates welcome_email_sent_at on success so we don't dupe."""
    settings = get_settings()
    subject, html, text = welcome_email(
        email=entry.email,
        position=entry.position,
        site_url=settings.site_url,
        founders_cap=settings.founders_seat_cap,
    )
    result = await send_email(
        to=entry.email,
        subject=subject,
        html=html,
        text=text,
        tags={"category": "waitlist_welcome", "position": str(entry.position)},
    )
    if result.delivered:
        entry.welcome_email_sent_at = func.now()
        await session.flush()


# ---------------------------------------------------------------------------
# Direct endpoint (landing page JS → API)
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=WaitlistJoinResponse,
    status_code=status.HTTP_201_CREATED,
)
async def join(
    req: WaitlistJoinRequest,
    session: SessionDep,
) -> WaitlistJoinResponse:
    """Public endpoint — accepts email from landing page form."""
    return await _join_waitlist(req=req, session=session)


# ---------------------------------------------------------------------------
# Stats endpoint — powers the landing page counter
# ---------------------------------------------------------------------------

@router.get("/stats", response_model=WaitlistStats)
async def stats(session: SessionDep) -> WaitlistStats:
    """Lightweight, cache-friendly — safe to hit on every landing page load.

    Could be cached in Redis for 60s once traffic picks up; skipped for now.
    """
    settings = get_settings()
    count_stmt = select(func.count()).select_from(WaitlistEntry)
    total = int((await session.execute(count_stmt)).scalar_one() or 0)
    remaining = max(0, settings.founders_seat_cap - total)
    return WaitlistStats(total=total, remaining_founders_seats=remaining)


# ---------------------------------------------------------------------------
# Tally.so webhook — signed payloads
# ---------------------------------------------------------------------------

class _TallyFieldValue(BaseModel):
    """Tally sends form answers as a list of {key, label, type, value} entries."""
    key: str | None = None
    label: str | None = None
    type: str | None = None
    value: Any = None


class _TallyPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    event_id: str | None = Field(default=None, alias="eventId")
    event_type: str | None = Field(default=None, alias="eventType")
    created_at: str | None = Field(default=None, alias="createdAt")
    data: dict[str, Any]


def _verify_tally_signature(body: bytes, signature: str | None, secret: str) -> bool:
    """Tally signs webhooks with HMAC-SHA256 over the raw body.

    Header: `Tally-Signature: <hex>`
    """
    if not signature or not secret:
        return False
    expected = hmac.new(
        secret.encode("utf-8"), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def _extract_email_from_tally(payload: _TallyPayload) -> str | None:
    """Tally's payload shape: data.fields is a list of answered questions."""
    fields = payload.data.get("fields", []) or []
    for f in fields:
        try:
            fv = _TallyFieldValue(**f)
        except Exception:
            continue
        label_or_key = (fv.label or fv.key or "").lower()
        # Match by label containing 'email' OR by type='INPUT_EMAIL'
        is_email_field = (
            fv.type == "INPUT_EMAIL" or "email" in label_or_key or "邮箱" in label_or_key
        )
        if is_email_field and isinstance(fv.value, str) and "@" in fv.value:
            return fv.value.strip().lower()
    return None


@router.post("/tally", status_code=status.HTTP_200_OK)
async def tally_webhook(
    request: Request,
    session: SessionDep,
) -> dict[str, Any]:
    """Tally.so webhook receiver.

    Configure at Tally → Form → Integrations → Webhooks:
      URL    = https://api.trendradar.app/api/v1/waitlist/tally
      Secret = $TALLY_SIGNING_SECRET (env var)
    """
    settings = get_settings()
    raw = await request.body()
    signature = request.headers.get("tally-signature")

    # Allow unsigned in dev so local testing with curl works
    if settings.tally_signing_secret:
        if not _verify_tally_signature(raw, signature, settings.tally_signing_secret):
            logger.warning("Tally webhook: bad or missing signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
    else:
        logger.warning("TALLY_SIGNING_SECRET not set — accepting webhook unsigned (dev only)")

    try:
        payload = _TallyPayload.model_validate_json(raw)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Bad payload: {e}") from e

    email = _extract_email_from_tally(payload)
    if not email:
        raise HTTPException(status_code=400, detail="No email field found in submission")

    meta = {
        "tally_event_id": payload.event_id,
        "tally_event_type": payload.event_type,
    }
    req = WaitlistJoinRequest(email=email, source="tally", metadata=meta)
    result = await _join_waitlist(req=req, session=session)
    # Tally docs recommend returning 200 with a small body for success
    return {"ok": True, "position": result.position, "already": result.already_registered}
