"""Pydantic request/response schemas for chat endpoints."""
from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None  # new session if None


class Pick(BaseModel):
    product_id: str
    rank: int
    score: float
    why_now: str
    rationale: str
    risks: list[str] = []
    action: str


class PickerResponse(BaseModel):
    picks: list[Pick]
    summary: str
    model: str
    tokens_input: int
    tokens_output: int
