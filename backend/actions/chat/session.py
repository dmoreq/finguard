"""In-memory chat session store."""

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


_store: dict[str, ChatSession] = {}


def get_session(sender_id: str, user_id: str) -> ChatSession:
    if sender_id not in _store:
        _store[sender_id] = ChatSession(user_id=user_id)
    session = _store[sender_id]
    if session.user_id != user_id:
        session.user_id = user_id
    return session


def clear_sessions() -> None:
    """Test helper."""
    _store.clear()
