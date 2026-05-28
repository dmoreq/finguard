"""Chat session persistence."""

from __future__ import annotations

import json
from typing import Protocol

from actions.chat.domain.session import ChatSession
from actions.db.client import get_db
from actions.db.queries import clear_chat_sessions, get_chat_session_row, upsert_chat_session


class SessionStore(Protocol):
    async def get(self, sender_id: str, user_id: str) -> ChatSession:
        """Load or create a session for the webhook sender."""
        ...

    async def save(self, sender_id: str, session: ChatSession) -> None:
        """Persist session state."""
        ...

    async def clear_all(self) -> None:
        """Remove all sessions (tests)."""
        ...


class SqliteSessionStore:
    """SQLite-backed session store with in-process cache."""

    def __init__(self) -> None:
        self._cache: dict[str, ChatSession] = {}

    async def get(self, sender_id: str, user_id: str) -> ChatSession:
        if sender_id in self._cache:
            session = self._cache[sender_id]
            if session.user_id != user_id:
                session.user_id = user_id
            return session

        async with get_db() as conn:
            row = await get_chat_session_row(conn, sender_id)

        if row is not None:
            state = json.loads(str(row["state_json"]))
            session = ChatSession.model_validate({**state, "user_id": row["user_id"]})
            self._cache[sender_id] = session
            return session

        session = ChatSession(user_id=user_id)
        self._cache[sender_id] = session
        return session

    async def save(self, sender_id: str, session: ChatSession) -> None:
        self._cache[sender_id] = session
        payload = session.model_dump()
        async with get_db() as conn:
            await upsert_chat_session(
                conn,
                sender_id,
                session.user_id,
                json.dumps(payload),
            )

    async def clear_all(self) -> None:
        self._cache.clear()
        async with get_db() as conn:
            await clear_chat_sessions(conn)


_default_store: SessionStore | None = None


def get_session_store() -> SessionStore:
    global _default_store
    if _default_store is None:
        _default_store = SqliteSessionStore()
    return _default_store


def set_session_store(store: SessionStore) -> None:
    global _default_store
    _default_store = store


async def get_session(sender_id: str, user_id: str) -> ChatSession:
    return await get_session_store().get(sender_id, user_id)


async def save_session(sender_id: str, session: ChatSession) -> None:
    await get_session_store().save(sender_id, session)


async def clear_sessions() -> None:
    await get_session_store().clear_all()
