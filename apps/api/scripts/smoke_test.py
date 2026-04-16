"""Smoke tests — run after setup to verify each layer works.

Usage (from apps/api/):
    .\.venv\Scripts\Activate.ps1
    python scripts/smoke_test.py

Expected output:
    [1/4] ✓ Config loads
    [2/4] ✓ Database connects (1 row returned)
    [3/4] ✓ LLM Router responds
    [4/4] ✓ FastAPI app imports

Runs against whatever is configured in .env — local Postgres/Redis via docker-compose
by default. Uses a tiny DeepSeek call to verify the API key works.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Make `app` importable no matter where we run from
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


async def test_config() -> None:
    from app.core.config import get_settings
    s = get_settings()
    assert s.database_url, "DATABASE_URL missing"
    print(f"[1/4] ✓ Config loads  (env={s.app_env}, db={'set' if s.database_url else 'missing'})")


async def test_db() -> None:
    from sqlalchemy import text
    from app.core.db import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        row = (await session.execute(text("SELECT 1 as n"))).first()
        assert row and row.n == 1
    print("[2/4] ✓ Database connects  (SELECT 1 returned 1)")


async def test_llm() -> None:
    from app.core.llm_router import LLMMessage, router
    from app.core.config import get_settings
    s = get_settings()
    if not s.deepseek_api_key and not s.anthropic_api_key:
        print("[3/4] ⚠ Skipped — no LLM keys configured")
        return
    msgs = [
        LLMMessage(role="system", content="你是测试助手，回复一个字：ok"),
        LLMMessage(role="user", content="ping"),
    ]
    result = await router.complete(msgs, plan="free", max_tokens=20)
    assert result.text, "Empty LLM response"
    print(f"[3/4] ✓ LLM Router responds  (model={result.model}, got: {result.text[:40]!r})")


async def test_app() -> None:
    from app.main import app
    # FastAPI app object has a .router attribute
    assert hasattr(app, "router")
    routes = [r.path for r in app.routes if hasattr(r, "path")]
    must_have = ["/api/v1/health", "/api/v1/chat/query"]
    for m in must_have:
        assert m in routes, f"Missing route: {m}"
    print(f"[4/4] ✓ FastAPI app imports  ({len(routes)} routes registered)")


async def main() -> int:
    tests = [
        ("config", test_config),
        ("db", test_db),
        ("llm", test_llm),
        ("app", test_app),
    ]
    failures = 0
    for name, fn in tests:
        try:
            await fn()
        except Exception as e:
            failures += 1
            print(f"[✗] {name} failed: {e.__class__.__name__}: {e}")
    if failures:
        print(f"\n{failures} test(s) failed — see errors above")
        return 1
    print("\n🎉 All smoke tests passed. MVP backend is ready to go.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
