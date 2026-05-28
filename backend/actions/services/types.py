"""Shared types for chat services."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SessionUpdates(BaseModel):
    """Fields to merge into chat session after a service call."""

    confirmation_pending: bool | None = None
    last_transaction_id: str | None = None
    partial_transaction: dict[str, Any] | None = None
    dialogue_phase: str | None = None
    clear_partial: bool = False


class ServiceResult(BaseModel):
    """Webhook messages plus optional session mutations."""

    messages: list[dict[str, Any]] = Field(default_factory=list)
    session: SessionUpdates | None = None
