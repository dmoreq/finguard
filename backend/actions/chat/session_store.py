"""Chat session persistence (in-memory; SQLite store planned in P2)."""

from __future__ import annotations

from typing import Protocol

from actions.chat.domain.session import ChatSession


class SessionStore(Protocol):
    def get(self, sender_id: str, user_id: str) -> ChatSession:
        """Load or create a session for the webhook sender."""
        ...

    def clear_all(self) -> None:
        """Remove all sessions (tests)."""
        ...


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, ChatSession] = {}

    def get(self, sender_id: str, user_id: str) -> ChatSession:
        if sender_id not in self._sessions:
            self._sessions[sender_id] = ChatSession(user_id=user_id)
        session = self._sessions[sender_id]
        if session.user_id != user_id:
            session.user_id = user_id
        return session

    def clear_all(self) -> None:
        self._sessions.clear()


_default_store = InMemorySessionStore()


def get_session_store() -> SessionStore:
    return _default_store


def get_session(sender_id: str, user_id: str) -> ChatSession:
    return _default_store.get(sender_id, user_id)


def clear_sessions() -> None:
    _default_store.clear_all()
