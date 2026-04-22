"""Thin Resend API wrapper — only what we need for transactional email.

Uses the REST API directly (https://resend.com/docs/api-reference/emails/send-email)
instead of the `resend` SDK, to keep our dependency surface small and avoid blocking
I/O inside async handlers.

In dev (`send_emails=False`) we log the payload and return a fake id — so nothing
leaves the machine and tests don't need a mock server.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_RESEND_URL = "https://api.resend.com/emails"


@dataclass
class EmailSendResult:
    id: str
    delivered: bool  # False = dev mode or failure
    error: str | None = None


async def send_email(
    *,
    to: str,
    subject: str,
    html: str,
    text: str | None = None,
    tags: dict[str, str] | None = None,
) -> EmailSendResult:
    """Send a single transactional email via Resend.

    Returns an EmailSendResult — never raises. Callers can inspect `delivered`
    and `error` to decide whether to retry or surface the failure to the user.
    """
    settings = get_settings()

    # Dev / preview / missing-key fallback → log + pretend success
    if not settings.send_emails or not settings.resend_api_key:
        logger.info(
            "📧 [dry-run] Skipping send (SEND_EMAILS=%s, key_set=%s) → to=%s subject=%r",
            settings.send_emails,
            bool(settings.resend_api_key),
            to,
            subject,
        )
        return EmailSendResult(id="dryrun-" + to, delivered=False)

    payload: dict[str, Any] = {
        "from": settings.resend_from_email,
        "to": [to],
        "subject": subject,
        "html": html,
    }
    if text:
        payload["text"] = text
    if settings.resend_reply_to:
        payload["reply_to"] = settings.resend_reply_to
    if tags:
        # Resend wants a list of {name, value}
        payload["tags"] = [{"name": k, "value": v} for k, v in tags.items()]

    headers = {
        "Authorization": f"Bearer {settings.resend_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(_RESEND_URL, json=payload, headers=headers)
            if resp.status_code >= 400:
                logger.warning("Resend send failed: %s %s", resp.status_code, resp.text)
                return EmailSendResult(id="", delivered=False, error=resp.text[:300])
            data = resp.json()
            msg_id = data.get("id", "")
            logger.info("📧 Resend delivered id=%s to=%s", msg_id, to)
            return EmailSendResult(id=msg_id, delivered=True)
    except httpx.HTTPError as e:
        logger.exception("Resend transport error")
        return EmailSendResult(id="", delivered=False, error=str(e))
