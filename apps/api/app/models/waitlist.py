"""Waitlist entries — collected before product launch, migrated to `users` on signup."""
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class WaitlistEntry(Base):
    __tablename__ = "waitlist"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    # Nth person to join — used in Email 1 for "you're #247 on the waitlist"
    position: Mapped[int] = mapped_column(Integer, index=True)
    # Attribution — where did this signup come from?
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)  # utm_source
    referrer: Mapped[str | None] = mapped_column(String(512), nullable=True)  # document.referrer
    # Anything else the form sent us (utm_medium, utm_campaign, experiment buckets, etc.)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    # When they convert to a real paying user, we link back
    converted_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # Resend idempotency — don't re-send welcome if this is set
    welcome_email_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
