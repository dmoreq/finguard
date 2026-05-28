"""In-memory chat session model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChatSession(BaseModel):
    user_id: str
    dialogue_phase: str = "idle"
    confirmation_pending: bool = False
    last_transaction_id: str | None = None
    partial_transaction: dict[str, Any] = Field(default_factory=dict)
    chat_history: list[tuple[str, str]] = Field(default_factory=list)

    def append_turn(self, role: str, content: str, limit: int = 10) -> None:
        self.chat_history.append((role, content))
        if len(self.chat_history) > limit:
            self.chat_history = self.chat_history[-limit:]
