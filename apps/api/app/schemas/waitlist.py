"""Pydantic I/O for waitlist endpoints."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class WaitlistJoinRequest(BaseModel):
    """Public request body — sent directly from the landing page or via Tally webhook.

    Kept loose: only email is required; attribution fields are optional.
    """
    email: EmailStr
    source: str | None = Field(default=None, max_length=64)
    referrer: str | None = Field(default=None, max_length=512)
    metadata: dict[str, Any] | None = None

    # Accept `metadata` in the request body but store as `metadata_json` in DB.
    model_config = ConfigDict(populate_by_name=True)


class WaitlistJoinResponse(BaseModel):
    """What we send back after a successful join.

    Position is what lets the landing page render "You're #247 — locked in".
    """
    id: UUID
    email: EmailStr
    position: int
    created_at: datetime
    already_registered: bool = False


class WaitlistStats(BaseModel):
    """Lightweight public stats for landing page (no PII)."""
    total: int
    remaining_founders_seats: int  # out of 100 lifetime-50%-off slots
