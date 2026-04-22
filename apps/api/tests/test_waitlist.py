"""Unit tests for the waitlist logic.

Focuses on pure functions so no DB / network setup needed. Integration tests
against a real Postgres come in a later commit once we have a test fixture.

Run: `pytest apps/api/tests/test_waitlist.py -v`
"""
from __future__ import annotations

import hashlib
import hmac

import pytest

from app.api.v1.waitlist import (
    _TallyPayload,
    _extract_email_from_tally,
    _verify_tally_signature,
)
from app.integrations.email_templates import welcome_email


# ---------------------------------------------------------------------------
# Tally webhook parsing
# ---------------------------------------------------------------------------

def test_extract_email_by_type():
    payload = _TallyPayload(
        eventId="evt_1",
        eventType="FORM_RESPONSE",
        data={
            "fields": [
                {"key": "q1", "label": "What's your name?", "type": "INPUT_TEXT", "value": "Jane"},
                {"key": "q2", "label": "Email", "type": "INPUT_EMAIL", "value": "JANE@TEST.COM"},
            ]
        },
    )
    assert _extract_email_from_tally(payload) == "jane@test.com"


def test_extract_email_by_label_chinese():
    """Some Tally forms use Chinese labels; fall back to label matching."""
    payload = _TallyPayload(
        data={
            "fields": [
                {"key": "q1", "label": "你的邮箱", "type": "INPUT_TEXT", "value": "seller@tiktok.cn"},
            ]
        },
    )
    assert _extract_email_from_tally(payload) == "seller@tiktok.cn"


def test_extract_email_missing():
    payload = _TallyPayload(data={"fields": [{"key": "q1", "label": "Name", "value": "Bob"}]})
    assert _extract_email_from_tally(payload) is None


def test_extract_email_no_fields():
    payload = _TallyPayload(data={})
    assert _extract_email_from_tally(payload) is None


# ---------------------------------------------------------------------------
# HMAC signature verification
# ---------------------------------------------------------------------------

def _sign(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def test_signature_valid():
    body = b'{"hello":"world"}'
    sig = _sign("s3cret", body)
    assert _verify_tally_signature(body, sig, "s3cret") is True


def test_signature_wrong_secret():
    body = b'{"hello":"world"}'
    sig = _sign("wrong", body)
    assert _verify_tally_signature(body, sig, "s3cret") is False


def test_signature_missing():
    assert _verify_tally_signature(b"anything", None, "s3cret") is False


def test_signature_tampered_body():
    body = b'{"hello":"world"}'
    sig = _sign("s3cret", body)
    tampered = b'{"hello":"evil"}'
    assert _verify_tally_signature(tampered, sig, "s3cret") is False


# ---------------------------------------------------------------------------
# Welcome email rendering
# ---------------------------------------------------------------------------

def test_welcome_email_founder():
    subject, html, text = welcome_email(
        email="a@b.com",
        position=47,
        site_url="https://trendradar.app",
        founders_cap=100,
    )
    assert "终身 5 折" in subject
    assert "#47" in html
    assert "¥449/年" in html
    assert "https://trendradar.app/alternatives" in html
    assert "#47" in text
    assert "¥449/年" in text


def test_welcome_email_non_founder():
    subject, html, text = welcome_email(
        email="a@b.com",
        position=250,
        site_url="https://trendradar.app",
        founders_cap=100,
    )
    # Subject switches when past the founders cap
    assert "终身 5 折" not in subject
    assert "waitlist" in subject.lower()
    assert "首月 ¥49" in html


@pytest.mark.parametrize(
    "pos,founders_cap,should_be_founder",
    [
        (1, 100, True),
        (100, 100, True),    # 100th person is still a founder (inclusive)
        (101, 100, False),
        (1, 50, True),
        (51, 50, False),
    ],
)
def test_founder_cap_boundary(pos, founders_cap, should_be_founder):
    subject, html, _ = welcome_email(
        email="x@y.com",
        position=pos,
        site_url="https://example.com",
        founders_cap=founders_cap,
    )
    if should_be_founder:
        assert "¥449" in html, f"pos {pos} should be founder"
    else:
        assert "¥449" not in html, f"pos {pos} should NOT be founder"
