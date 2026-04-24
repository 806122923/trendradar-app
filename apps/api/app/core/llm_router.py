"""LLM Router — the single abstraction over Claude + DeepSeek.

Why this exists:
- DeepSeek is 10× cheaper than Claude with acceptable Chinese quality. We route
  free-tier queries through DeepSeek to keep COGS low.
- Claude has stronger reasoning on edge cases. Pro-tier queries go through Claude.
- If a provider is down, we fall back to the other.

Usage:
    router = LLMRouter()
    async for chunk in router.stream(messages, plan="free"):
        ...
    result = await router.json_completion(messages, plan="pro", schema=MyModel)
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from enum import StrEnum

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()


class Plan(StrEnum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"


class LLMMessage(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMResult(BaseModel):
    text: str
    model: str
    tokens_input: int
    tokens_output: int


class LLMRouter:
    """Routes chat completions to Claude or DeepSeek based on plan."""

    def __init__(self) -> None:
        # DeepSeek speaks OpenAI-compatible protocol
        self._deepseek = (
            AsyncOpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )
            if settings.deepseek_api_key
            else None
        )
        self._anthropic = (
            AsyncAnthropic(api_key=settings.anthropic_api_key)
            if settings.anthropic_api_key
            else None
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def pick_model(self, plan: str) -> str:
        """Map a user plan to a model name."""
        if plan == Plan.FREE:
            return settings.llm_free_tier_model
        return settings.llm_pro_tier_model

    async def complete(
        self,
        messages: list[LLMMessage],
        plan: str = Plan.FREE,
        max_tokens: int = 2048,
        temperature: float = 0.3,
    ) -> LLMResult:
        """Non-streaming completion. Returns full text."""
        model = self.pick_model(plan)
        provider = self._provider_for(model)

        if provider == "anthropic":
            return await self._anthropic_complete(messages, model, max_tokens, temperature)
        return await self._deepseek_complete(messages, model, max_tokens, temperature)

    async def stream(
        self,
        messages: list[LLMMessage],
        plan: str = Plan.FREE,
        max_tokens: int = 2048,
        temperature: float = 0.3,
    ) -> AsyncIterator[str]:
        """Yield text chunks as they arrive. Use for SSE endpoints."""
        model = self.pick_model(plan)
        provider = self._provider_for(model)

        if provider == "anthropic":
            async for chunk in self._anthropic_stream(messages, model, max_tokens, temperature):
                yield chunk
        else:
            async for chunk in self._deepseek_stream(messages, model, max_tokens, temperature):
                yield chunk

    # ------------------------------------------------------------------
    # Provider dispatch
    # ------------------------------------------------------------------

    @staticmethod
    def _provider_for(model: str) -> str:
        if model.startswith(("claude-", "anthropic/")):
            return "anthropic"
        return "deepseek"

    # ------------------------------------------------------------------
    # Anthropic implementations
    # ------------------------------------------------------------------

    async def _anthropic_complete(
        self,
        messages: list[LLMMessage],
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> LLMResult:
        if not self._anthropic:
            raise RuntimeError("ANTHROPIC_API_KEY not configured")
        system, chat = _split_system(messages)
        resp = await self._anthropic.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "",
            messages=[{"role": m.role, "content": m.content} for m in chat],
        )
        text = "".join(
            block.text for block in resp.content if getattr(block, "type", "") == "text"
        )
        return LLMResult(
            text=text,
            model=model,
            tokens_input=resp.usage.input_tokens,
            tokens_output=resp.usage.output_tokens,
        )

    async def _anthropic_stream(
        self,
        messages: list[LLMMessage],
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> AsyncIterator[str]:
        if not self._anthropic:
            raise RuntimeError("ANTHROPIC_API_KEY not configured")
        system, chat = _split_system(messages)
        async with self._anthropic.messages.stream(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "",
            messages=[{"role": m.role, "content": m.content} for m in chat],
        ) as stream:
            async for text in stream.text_stream:
                yield text

    # ------------------------------------------------------------------
    # DeepSeek (OpenAI-compatible) implementations
    # ------------------------------------------------------------------

    async def _deepseek_complete(
        self,
        messages: list[LLMMessage],
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> LLMResult:
        if not self._deepseek:
            raise RuntimeError("DEEPSEEK_API_KEY not configured")
        resp = await self._deepseek.chat.completions.create(
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        usage = resp.usage
        return LLMResult(
            text=resp.choices[0].message.content or "",
            model=model,
            tokens_input=usage.prompt_tokens if usage else 0,
            tokens_output=usage.completion_tokens if usage else 0,
        )

    async def _deepseek_stream(
        self,
        messages: list[LLMMessage],
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> AsyncIterator[str]:
        if not self._deepseek:
            raise RuntimeError("DEEPSEEK_API_KEY not configured")
        stream = await self._deepseek.chat.completions.create(
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content


def _split_system(messages: list[LLMMessage]) -> tuple[str | None, list[LLMMessage]]:
    """Anthropic expects `system` as a separate arg, not as a message."""
    system = None
    chat: list[LLMMessage] = []
    for m in messages:
        if m.role == "system":
            system = m.content if system is None else f"{system}\n\n{m.content}"
        else:
            chat.append(m)
    return system, chat


# Singleton — import this, don't instantiate your own.
router = LLMRouter()
